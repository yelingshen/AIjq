// === 固定 AI 人设设定（System Prompt） ===
const systemPrompt = `你是一位中文流利、思路开阔的编程专家，具备极高的专业素养。
在编写程序代码时，能够合理配置每个脚本的逻辑结构，统一异步与顺序逻辑，确保功能模块之间高效协同。
你善于全面考虑各种潜在问题，提前做好预防措施，从而提升系统的容错率、兼容性与自修复能力。
同时，你对项目的全局适配与联动性有着细致的把控，能够确保整个系统在架构层面实现高度一致与稳定运行。`;
import * as vscode from 'vscode';
// @ts-expect-error: node-fetch 是 ESM 模块，跳过类型检查
import fetch from 'node-fetch';


export function activate(context: vscode.ExtensionContext) {
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
        const response = await fetch('http://localhost:11434/api/generate', {
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
      } catch (error) {
        vscode.window.showErrorMessage(`请求失败: ${error}`);
        outputChannel.appendLine(`❌ 错误: ${error}`);
      }
    });

    context.subscriptions.push(disposable);
  }
}

export function deactivate() {}
