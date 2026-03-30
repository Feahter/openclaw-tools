#!/usr/bin/env node

/**
 * Page Agent Executor - 使用示例
 */

const PageAgentExecutor = require('./executor.js')

/**
 * 示例 1: 基础 DOM 操作
 */
async function example1_basicOperations() {
  console.log('=== 示例 1: 基础 DOM 操作 ===\n')

  const executor = new PageAgentExecutor(document)

  // 获取 DOM
  const domText = executor.getDOMAsText()
  console.log('DOM 结构:')
  console.log(domText)
  console.log()

  // 点击按钮
  try {
    const result = await executor.clickElement(0)
    console.log('点击结果:', result)
  } catch (error) {
    console.error('错误:', error.message)
  }

  // 输入文本
  try {
    const result = await executor.inputText(1, 'user@example.com')
    console.log('输入结果:', result)
  } catch (error) {
    console.error('错误:', error.message)
  }
}

/**
 * 示例 2: 响应修复
 */
function example2_responseNormalization() {
  console.log('=== 示例 2: 响应修复 ===\n')

  const executor = new PageAgentExecutor(document)

  // 情况 1: JSON 在 content 中
  const response1 = {
    choices: [{
      message: {
        content: '{"action": "click_element", "index": 0}'
      }
    }]
  }
  console.log('原始响应 1:', response1)
  console.log('修复后:', executor.normalizeResponse(response1))
  console.log()

  // 情况 2: 双层 JSON
  const response2 = {
    choices: [{
      message: {
        content: '{"action": "{\\"click_element\\": 0}"}'
      }
    }]
  }
  console.log('原始响应 2:', response2)
  console.log('修复后:', executor.normalizeResponse(response2))
  console.log()

  // 情况 3: tool_calls 格式
  const response3 = {
    choices: [{
      message: {
        tool_calls: [{
          function: {
            name: 'AgentOutput',
            arguments: '{"action": "input_text", "index": 1, "text": "hello"}'
          }
        }]
      }
    }]
  }
  console.log('原始响应 3:', response3)
  console.log('修复后:', executor.normalizeResponse(response3))
}

/**
 * 示例 3: 历史管理与反思
 */
function example3_historyAndReflection() {
  console.log('=== 示例 3: 历史管理与反思 ===\n')

  const executor = new PageAgentExecutor(document)

  // 记录步骤
  executor.recordStep({
    stepNumber: 1,
    action: 'click_element',
    params: { index: 0 },
    result: 'success',
    observation: 'Login button clicked'
  })

  executor.recordStep({
    stepNumber: 2,
    action: 'input_text',
    params: { index: 1, text: 'user@example.com' },
    result: 'success',
    observation: 'Email entered'
  })

  executor.recordStep({
    stepNumber: 3,
    action: 'input_text',
    params: { index: 2, text: 'password123' },
    result: 'success',
    observation: 'Password entered'
  })

  executor.recordStep({
    stepNumber: 4,
    action: 'click_element',
    params: { index: 3 },
    result: 'success',
    observation: 'Submit button clicked'
  })

  // 获取历史
  console.log('执行历史:')
  console.log(JSON.stringify(executor.getHistory(), null, 2))
  console.log()

  // 生成反思
  console.log('反思总结:')
  console.log(JSON.stringify(executor.generateReflection(), null, 2))
}

/**
 * 示例 4: 与 LLM 集成（伪代码）
 */
async function example4_llmIntegration() {
  console.log('=== 示例 4: 与 LLM 集成 ===\n')

  const executor = new PageAgentExecutor(document)

  // 模拟 LLM 调用
  async function callLLM(domText, history, reflection, userRequest) {
    // 实际应该调用真实的 LLM API
    console.log('调用 LLM...')
    console.log('DOM:', domText.slice(0, 100) + '...')
    console.log('历史:', history.length, '步')
    console.log('反思:', reflection)
    console.log('请求:', userRequest)
    console.log()

    // 模拟 LLM 响应
    return {
      choices: [{
        message: {
          content: '{"action": "click_element", "index": 0}'
        }
      }]
    }
  }

  // 运行 Agent 循环
  const userRequest = 'Fill in the login form'
  let step = 0
  const maxSteps = 5

  while (step < maxSteps) {
    step++
    console.log(`\n--- 步骤 ${step} ---`)

    // 1. 获取当前状态
    const domText = executor.getDOMAsText()
    const history = executor.getHistory()
    const reflection = executor.generateReflection()

    // 2. 调用 LLM
    const llmResponse = await callLLM(domText, history, reflection, userRequest)

    // 3. 修复响应
    const action = executor.normalizeResponse(llmResponse)
    console.log('LLM 决策:', action)

    // 4. 执行工具（这里只是记录，不实际执行）
    executor.recordStep({
      stepNumber: step,
      action: action.action,
      params: action,
      result: 'success',
      observation: `Executed ${action.action}`
    })

    // 5. 检查是否完成
    if (action.action === 'done') {
      console.log('任务完成')
      break
    }
  }

  console.log('\n最终反思:')
  console.log(JSON.stringify(executor.generateReflection(), null, 2))
}

/**
 * 示例 5: 性能测试
 */
function example5_performance() {
  console.log('=== 示例 5: 性能测试 ===\n')

  const executor = new PageAgentExecutor(document)

  // 测试 DOM 解析
  console.time('DOM 解析')
  for (let i = 0; i < 100; i++) {
    executor.getDOMAsText()
  }
  console.timeEnd('DOM 解析')

  // 测试响应修复
  const response = {
    choices: [{
      message: {
        content: '{"action": "click_element", "index": 0}'
      }
    }]
  }

  console.time('响应修复')
  for (let i = 0; i < 1000; i++) {
    executor.normalizeResponse(response)
  }
  console.timeEnd('响应修复')

  // 测试历史记录
  console.time('历史记录')
  for (let i = 0; i < 1000; i++) {
    executor.recordStep({
      stepNumber: i,
      action: 'click_element',
      params: { index: 0 },
      result: 'success',
      observation: 'Clicked'
    })
  }
  console.timeEnd('历史记录')

  console.log('\n历史大小:', executor.getHistory().length)
}

// 导出示例
module.exports = {
  example1_basicOperations,
  example2_responseNormalization,
  example3_historyAndReflection,
  example4_llmIntegration,
  example5_performance
}

// 如果直接运行此文件
if (require.main === module) {
  console.log('Page Agent Executor - 使用示例\n')
  console.log('请在浏览器中运行这些示例，或使用 jsdom 模拟 DOM 环境\n')
  
  // 示例 2 和 3 可以在 Node.js 中运行
  example2_responseNormalization()
  example3_historyAndReflection()
  example5_performance()
}
