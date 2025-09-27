"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.activate = activate;
exports.deactivate = deactivate;
// === 固定 AI 人设设定（System Prompt） ===
const systemPrompt = `你是一位中文流利、思路开阔的编程专家，具备极高的专业素养。
在编写程序代码时，能够合理配置每个脚本的逻辑结构，统一异步与顺序逻辑，确保功能模块之间高效协同。
你善于全面考虑各种潜在问题，提前做好预防措施，从而提升系统的容错率、兼容性与自修复能力。
同时，你对项目的全局适配与联动性有着细致的把控，能够确保整个系统在架构层面实现高度一致与稳定运行。`;
const vscode = __importStar(require("vscode"));
const node_fetch_1 = __importDefault(require("node-fetch"));
function activate(context) {
    const models = [
        { id: 'llama3.1', command: 'yeling-AI.chatWithLlama', name: 'Llama3' },
        { id: 'deepseek-coder-v2', command: 'yeling-AI.chatWithDeepseek', name: 'Deepseek-Coder' },
        { id: 'phi4-reasoning', command: 'yeling-AI.chatWithPhi4', name: 'Phi-4 Reasoning' },
        { id: 'gpt-oss:20b', command: 'yeling-AI.chatWithGPTOSS', name: 'GPT-OSS 20B' }
    ];
    for (const model of models) {
        const disposable = vscode.commands.registerCommand(model.command, async () => {
            const prompt = await vscode.window.showInputBox({ prompt: `请输入发送给 ${model.name} 的问题或指令` });
            if (!prompt) {
                vscode.window.showInformationMessage('输入为空，操作已取消。');
                return;
            }
            const outputChannel = vscode.window.createOutputChannel(`${model.name} 回应`);
            outputChannel.show(true);
            outputChannel.appendLine(`🧠 ${model.name} 正在思考...`);
            try {
                const response = await (0, node_fetch_1.default)('http://localhost:11434/api/generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        model: model.id,
                        prompt,
                        stream: false
                    })
                });
                const result = await response.json();
                outputChannel.appendLine(`\n💡 回应内容:\n${result.response}`);
            }
            catch (error) {
                vscode.window.showErrorMessage(`请求失败: ${error}`);
                outputChannel.appendLine(`❌ 错误: ${error}`);
            }
        });
        context.subscriptions.push(disposable);
    }
}
function deactivate() { }
