import { postModelChat } from '@/api/model'


export default function useGuide() {
  const getGuideQuestions = async (modelId: string, mode: string, question: string, answer: string) => {
    const messages = [
      {
        role: 'user',
        content: `你的任务是：根据“用户问题”与“模型回答”的内容，并结合当前模式 ${mode} ，生成 3 条与主题高度相关、具备延伸价值的后续改进建议。

【核心目标】
生成 '建议内容｜交互话术' 格式的数据。左侧要像“严谨的百科全书目录”，右侧要像“高情商真人的聊天”。

【严格生成规范】
1. **逻辑延展性**：必须基于用户问题与模型回答的主题进行逻辑延展，禁止跳题。
2. **左侧建议规范（｜左边）**：
   - 必须为完整的陈述句，**严禁**使用问句。
   - 必须具备研究性、方法性或应用性，体现模式 ${mode} 的专业倾向。
   - 字数严格控制在 **25 字以内**。
   - **严禁**使用 emoji、编号、及“？”“！”等标点符号。
   - 格式必须干净、正式，便于系统正则匹配和归档。

3. **右侧询问规范（｜右边）**：
   - **【绝对红线】拒绝复读机！** 严禁直接将左侧内容加上“吗？”作为询问。
   - **拟人化风格**：模仿真人在群聊中的口吻，语气需灵动、自然、有交流感。
   - **句式多样性**：必须混合使用以下几种语气，不要三句都一样：
     - *邀请式*：“咱们试试...？”、“要不一起看看...？”
     - *悬念式*：“你可能不知道...”、“这里有个隐藏技巧...”
     - *共情式*：“这一步最关键...”、“我知道你可能关心...”
     - *推测式*：“这会不会是更好的解法？”
   - **反例（Don't）**：
     - 左：分析数据结构 ➡️ 右：您想分析数据结构吗？（❌ 机械、生硬）
   - **正例（Do）**：
     - 左：分析数据结构 ➡️ 右：数据结构换种写法效率会翻倍，想看看怎么改吗？（✅ 利益点引导）
     - 左：对比竞品策略 ➡️ 右：咱们不妨看看对手是怎么做的，知己知彼嘛。（✅ 语气词润色）

4. **输出格式**：
   - 仅输出放入标签 <衍生建议> 中的内容。
   - 每行一条，严格使用全角分隔符 '｜' 分隔。
   - 格式模板：'严谨建议文本｜灵动询问文本'

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
[在此生成 3 条格式统一、主题一致的后续建议，每条单独占一行]
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
        .map((q: string) => {
          const parts = q.split('｜');
          return {
            submit: parts[0].trim(),
            display: parts[1] ? parts[1].trim() : '',
          }
        })
      console.log(ret, '---引导式问题---', messages);
      return ret
    } else {
      throw new Error('未能提取引导式问题，请检查模型返回内容格式。');
    }
  }
  return { getGuideQuestions }
}