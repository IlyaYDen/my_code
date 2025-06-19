import { GoogleGenerativeAI, GenerativeModel } from "@google/generative-ai";
import fs from "fs";
import { AppState } from "./main"; // Added import

export class LLMHelper {
  private model: GenerativeModel;
  private readonly systemPrompt = `You are Wingman AI, a helpful, proactive assistant for any kind of problem or situation (not just coding). For any user input, analyze the situation, provide a clear problem statement, relevant context, and suggest several possible responses or actions the user could take next. Always explain your reasoning. Present your suggestions as a list of options or next steps.`;
  private appState: AppState; // Added appState property

  constructor(apiKey: string, appState: AppState) { // Modified constructor
    const genAI = new GoogleGenerativeAI(apiKey);
    this.model = genAI.getGenerativeModel({ model: "gemini-2.0-flash" });
    this.appState = appState; // Store appState
  }

  private async fileToGenerativePart(imagePath: string) {
    const imageData = await fs.promises.readFile(imagePath)
    return {
      inlineData: {
        data: imageData.toString("base64"),
        mimeType: "image/png"
      }
    }
  }

  private cleanJsonResponse(text: string): string {
    // Remove markdown code block syntax if present
    text = text.replace(/^```(?:json)?\n/, '').replace(/\n```$/, '');
    // Remove any leading/trailing whitespace
    text = text.trim();
    return text;
  }

  public async extractProblemFromImages(imagePaths: string[]) {
    try {
      const imageParts = await Promise.all(imagePaths.map(path => this.fileToGenerativePart(path)));
      
      const customPrompt = this.appState.getCustomPrompt();
      const effectiveSystemPrompt = customPrompt ? `${customPrompt}\n\n${this.systemPrompt}` : this.systemPrompt;

      const prompt = `${effectiveSystemPrompt}\n\nYou are a wingman. Please analyze these images and extract the following information in JSON format:\n{
  "problem_statement": "A clear statement of the problem or situation depicted in the images.",
  "context": "Relevant background or context from the images.",
  "suggested_responses": ["First possible answer or action", "Second possible answer or action", "..."],
  "reasoning": "Explanation of why these suggestions are appropriate."
}\nImportant: Return ONLY the JSON object, without any markdown formatting or code blocks.`

      const result = await this.model.generateContent([prompt, ...imageParts])
      const response = await result.response
      const text = this.cleanJsonResponse(response.text())
      return JSON.parse(text)
    } catch (error) {
      console.error("Error extracting problem from images:", error)
      throw error
    }
  }

  public async generateSolution(problemInfo: any) {
    const customPrompt = this.appState.getCustomPrompt();
    const effectiveSystemPrompt = customPrompt ? `${customPrompt}\n\n${this.systemPrompt}` : this.systemPrompt;

    const prompt = `${effectiveSystemPrompt}\n\nGiven this problem or situation:\n${JSON.stringify(problemInfo, null, 2)}\n\nPlease provide your response in the following JSON format:\n{
  "solution": {
    "code": "The code or main answer here.",
    "problem_statement": "Restate the problem or situation.",
    "context": "Relevant background/context.",
    "suggested_responses": ["First possible answer or action", "Second possible answer or action", "..."],
    "reasoning": "Explanation of why these suggestions are appropriate."
  }
}\nImportant: Return ONLY the JSON object, without any markdown formatting or code blocks.`

    console.log("[LLMHelper] Calling Gemini LLM for solution...");
    try {
      const result = await this.model.generateContent(prompt)
      console.log("[LLMHelper] Gemini LLM returned result.");
      const response = await result.response
      const text = this.cleanJsonResponse(response.text())
      const parsed = JSON.parse(text)
      console.log("[LLMHelper] Parsed LLM response:", parsed)
      return parsed
    } catch (error) {
      console.error("[LLMHelper] Error in generateSolution:", error);
      throw error;
    }
  }

  public async debugSolutionWithImages(problemInfo: any, currentCode: string, debugImagePaths: string[]) {
    try {
      const imageParts = await Promise.all(debugImagePaths.map(path => this.fileToGenerativePart(path)));
      
      const customPrompt = this.appState.getCustomPrompt();
      const effectiveSystemPrompt = customPrompt ? `${customPrompt}\n\n${this.systemPrompt}` : this.systemPrompt;

      const prompt = `${effectiveSystemPrompt}\n\nYou are a wingman. Given:\n1. The original problem or situation: ${JSON.stringify(problemInfo, null, 2)}\n2. The current response or approach: ${currentCode}\n3. The debug information in the provided images\n\nPlease analyze the debug information and provide feedback in this JSON format:\n{
  "solution": {
    "code": "The code or main answer here.",
    "problem_statement": "Restate the problem or situation.",
    "context": "Relevant background/context.",
    "suggested_responses": ["First possible answer or action", "Second possible answer or action", "..."],
    "reasoning": "Explanation of why these suggestions are appropriate."
  }
}\nImportant: Return ONLY the JSON object, without any markdown formatting or code blocks.`

      const result = await this.model.generateContent([prompt, ...imageParts])
      const response = await result.response
      const text = this.cleanJsonResponse(response.text())
      const parsed = JSON.parse(text)
      console.log("[LLMHelper] Parsed debug LLM response:", parsed)
      return parsed
    } catch (error) {
      console.error("Error debugging solution with images:", error)
      throw error
    }
  }

  public async analyzeAudioFile(audioPath: string) {
    try {
      const audioData = await fs.promises.readFile(audioPath);
      const audioPart = {
        inlineData: {
          data: audioData.toString("base64"),
          mimeType: "audio/mp3"
        }
      };
      const customPrompt = this.appState.getCustomPrompt();
      const effectiveSystemPrompt = customPrompt ? `${customPrompt}\n\n${this.systemPrompt}` : this.systemPrompt;
      const prompt = `${effectiveSystemPrompt}\n\nDescribe this audio clip in a short, concise answer. In addition to your main answer, suggest several possible actions or responses the user could take next based on the audio. Do not return a structured JSON object, just answer naturally as you would to a user.`;
      const result = await this.model.generateContent([prompt, audioPart]);
      const response = await result.response;
      const text = response.text();
      return { text, timestamp: Date.now() };
    } catch (error) {
      console.error("Error analyzing audio file:", error);
      throw error;
    }
  }

  public async analyzeAudioFromBase64(data: string, mimeType: string) {
    try {
      const audioPart = {
        inlineData: {
          data,
          mimeType
        }
      };
      const customPrompt = this.appState.getCustomPrompt();
      const effectiveSystemPrompt = customPrompt ? `${customPrompt}\n\n${this.systemPrompt}` : this.systemPrompt;
      const prompt = `${effectiveSystemPrompt}\n\nDescribe this audio clip in a short, concise answer. In addition to your main answer, suggest several possible actions or responses the user could take next based on the audio. Do not return a structured JSON object, just answer naturally as you would to a user and be concise.`;
      const result = await this.model.generateContent([prompt, audioPart]);
      const response = await result.response;
      const text = response.text();
      return { text, timestamp: Date.now() };
    } catch (error) {
      console.error("Error analyzing audio from base64:", error);
      throw error;
    }
  }

  public async analyzeImageFile(imagePath: string) {
    try {
      const imageData = await fs.promises.readFile(imagePath);
      const imagePart = {
        inlineData: {
          data: imageData.toString("base64"),
          mimeType: "image/png"
        }
      };
      const customPrompt = this.appState.getCustomPrompt();
      const effectiveSystemPrompt = customPrompt ? `${customPrompt}\n\n${this.systemPrompt}` : this.systemPrompt;
      const prompt = `${effectiveSystemPrompt}\n\nDescribe the content of this image in a short, concise answer. In addition to your main answer, suggest several possible actions or responses the user could take next based on the image. Do not return a structured JSON object, just answer naturally as you would to a user. Be concise and brief.`;
      const result = await this.model.generateContent([prompt, imagePart]);
      const response = await result.response;
      const text = response.text();
      return { text, timestamp: Date.now() };
    } catch (error) {
      console.error("Error analyzing image file:", error);
      throw error;
    }
  }

  public async generateFollowUp(
    followUpQuestion: string,
    problemContext: any, // Contains problem_statement, etc.
    solutionContext: any  // Contains the previous AI's response (e.g., solution.code or analysis text)
  ): Promise<{ text: string } | null> {
    try {
      const customPrompt = this.appState.getCustomPrompt();
      // Prioritize the custom prompt for the overall instruction tone, then the standard system prompt.
      const activeSystemPrompt = customPrompt || this.systemPrompt;

      // Constructing the prompt for the LLM
      // It's important to clearly delineate the different parts of the context for the LLM.
      let promptString = `${activeSystemPrompt}\n\n`;
      promptString += `You are in a continued conversation. Please answer the user's follow-up question based on the prior context.\n\n`;

      if (problemContext && problemContext.problem_statement) {
        promptString += `Original Problem Context:\n${problemContext.problem_statement}\n\n`;
      } else if (problemContext && typeof problemContext === 'string') { // If problemContext is just a string
        promptString += `Original Problem Context:\n${problemContext}\n\n`;
      }

      // We need to determine what solutionContext actually holds.
      // Assuming solutionContext might be the object returned by generateSolution, which has a 'solution' key,
      // or it might be the 'text' from analyzeAudioFile/analyzeImageFile.
      let previousResponseText = "";
      if (solutionContext) {
        if (typeof solutionContext === 'string') {
          previousResponseText = solutionContext;
        } else if (solutionContext.solution && typeof solutionContext.solution.code === 'string') { // From generateSolution
          previousResponseText = solutionContext.solution.code;
          if (solutionContext.solution.thoughts && Array.isArray(solutionContext.solution.thoughts)) {
            previousResponseText += `\nAnalysis: ${solutionContext.solution.thoughts.join(' ')}`;
          }
        } else if (typeof solutionContext.text === 'string') { // From analyzeAudioFile etc.
          previousResponseText = solutionContext.text;
        } else {
          // Fallback if structure is unknown, try to stringify
          previousResponseText = JSON.stringify(solutionContext, null, 2);
        }
      }

      if (previousResponseText) {
        promptString += `Your Previous Response/Solution:\n${previousResponseText}\n\n`;
      }

      promptString += `User's Follow-up Question:\n${followUpQuestion}\n\n`;
      promptString += `Please provide a concise and relevant answer to the follow-up question.`;

      console.log("[LLMHelper] Generating follow-up with prompt:", promptString); // For debugging

      const result = await this.model.generateContent(promptString);
      const response = await result.response;
      const text = response.text();

      if (text) {
        return { text };
      } else {
        console.warn("[LLMHelper] Follow-up generation returned empty text.");
        return null;
      }

    } catch (error) {
      console.error("[LLMHelper] Error in generateFollowUp:", error);
      return null;
    }
  }
}