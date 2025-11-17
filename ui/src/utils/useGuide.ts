import { postModelChat } from '@/api/model'


export default function useGuide() {
  const getGuideQuestions = async (modelId: string, mode: string, question: string, answer: string) => {
    const messages = [
      {
        role: 'user',
        content: `你的任务是：根据“用户问题”与“模型回答”的内容，并结合当前模式 ${mode} ，生成 3 条与主题高度相关、具备延伸价值的后续改进建议。

【严格生成规范】
1. 必须基于用户问题与模型回答的主题进行逻辑延展，禁止跳题。
2. 建议内容必须具备研究性、方法性或应用性，不得输出泛泛而空的提问。
3. 每条建议需体现模式 ${mode} 的倾向，但不得显式提及模式名称。
4. 每条建议必须为完整陈述句（不是提问句，不以问号结尾）。
5. 每条建议不超过 25 字。
6. 禁止使用 emoji、编号、特殊符号（如“？”、“！”、“—”、“/” 等）。
7. 建议句式保持正式、可读、可归档，便于结构化处理。
8. 输出仅放入标签 <衍生建议> 中，每行一条。

以下是用户提出的问题：
<用户问题>
${question}
</用户问题>

以下是模型回答的内容：
<模型回答>
${answer}
</模型回答>

请依据以上内容，结合当前模式 ${mode} ，生成 3 条主题一致的后续改进建议。

<衍生建议>
[在此生成 3 条格式统一、主题一致、便于正则匹配的后续建议，每条单独占一行]
</衍生建议>
`,
      }
    ]
    const result = await postModelChat(modelId, { messages })
    console.log(result.data.content, '---引导式问题返回---', messages);
    const regex = /<衍生建议>\s*([\s\S]*?)\s*<\/衍生建议>/;
    const match = result.data.content.match(regex);
    if (match && match[1]) {
      const ret = match[1]
        .trim()
        .split('\n')
        .map((q: string) => q.trim())
      console.log(ret, '---引导式问题---', messages);
      return ret
    } else {
      throw new Error('未能提取引导式问题，请检查模型返回内容格式。');
    }
  }
  return { getGuideQuestions }
}