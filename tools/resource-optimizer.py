#!/usr/bin/env python3
"""
资源优化器 - 自主获取和优化商业/金融资源
功能：
1. API资源发现与评估
2. 商业机会识别
3. 效率优化建议
4. 自动化收益追踪
"""

import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

class ResourceOptimizer:
    def __init__(self):
        self.workspace = Path("/Users/fuzhuo/.openclaw/workspace")
        self.data_dir = self.workspace / "data"
        self.data_dir.mkdir(exist_ok=True)

        self.api_resources_file = self.data_dir / "api-resources.json"
        self.opportunities_file = self.data_dir / "business-opportunities.json"
        self.efficiency_metrics_file = self.data_dir / "efficiency-metrics.json"

        self.load_resources()

    def load_resources(self):
        """加载已有资源数据"""
        if self.api_resources_file.exists():
            with open(self.api_resources_file) as f:
                self.api_resources = json.load(f)
        else:
            self.api_resources = {
                "minimax": {"balance": 13.0, "priority": "high", "status": "active"},
                "groq": {"balance": "free tier", "priority": "high", "status": "active"},
                "together_ai": {"balance": "free tier", "priority": "mid", "status": "active"},
                "deepseek": {"balance": "backup", "priority": "low", "status": "standby"},
                "siliconflow": {"balance": "backup", "priority": "low", "status": "standby"}
            }

        if self.opportunities_file.exists():
            with open(self.opportunities_file) as f:
                self.opportunities = json.load(f)
        else:
            self.opportunities = []

    def save_resources(self):
        """保存资源数据"""
        with open(self.api_resources_file, 'w') as f:
            json.dump(self.api_resources, f, indent=2, ensure_ascii=False)

        with open(self.opportunities_file, 'w') as f:
            json.dump(self.opportunities, f, indent=2, ensure_ascii=False)

    def check_api_status(self):
        """检查API状态和余额"""
        print("\n🔍 API资源状态检查")
        print("=" * 50)

        # 更新Minimax状态（基于了解到的套餐信息）
        self.api_resources["minimax"] = {
            "balance": "Coding Plan (每5小时重置)",
            "type": "prompt-based",
            "prompt_limit": "未知",
            "priority": "high",
            "status": "active"
        }

        for api, info in self.api_resources.items():
            status = "✅" if info["status"] == "active" else "⏸️"
            if api == "minimax":
                print(f"{status} {api.upper()}: {info['balance']}")
                print(f"   类型: {info['type']} | 优先级: {info['priority']}")
            else:
                print(f"{status} {api.upper()}: {info['balance']} (优先级: {info['priority']})")

        # 检查是否需要充值
        balance = self.api_resources.get("minimax", {}).get("balance", "100")
        try:
            balance_val = int(float(balance))
        except (ValueError, TypeError):
            balance_val = 100
        if balance_val < 10:
            print("\n⚠️ 警告: Minimax余额低于¥10，需要充值!")

        # 提示套餐特点
        print("\n💡 Minimax套餐信息:")
        print("   - 按prompt计费 (1 prompt ≈ 15次模型调用)")
        print("   - 每5小时自动重置限额")
        print("   - 可切换到按量付费模式 (消耗账户余额)")
        print("   - 不支持退款，请合理规划使用")

        return self.api_resources

    def check_minimax_usage(self, api_key: str = None):
        """查询Minimax Coding Plan剩余额度"""
        print("\n📊 Minimax Coding Plan 用量查询")
        print("-" * 50)

        if not api_key:
            print("需要API Key才能查询用量")
            print("查询命令: curl https://www.minimaxi.com/v1/api/openplatform/coding_plan/remains")
            print("API文档: https://platform.minimaxi.com/docs/coding-plan/faq")
            return None

        import requests
        try:
            response = requests.get(
                'https://www.minimaxi.com/v1/api/openplatform/coding_plan/remains',
                headers={'Authorization': f'Bearer {api_key}'}
            )
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 剩余额度: {data}")
                return data
            else:
                print(f"❌ 查询失败: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ 错误: {e}")
            return None

    def discover_new_resources(self):
        """发现新资源"""
        print("\n🌐 发现新资源...")
        print("-" * 50)

        # 已知的免费/低成本资源
        new_resources = [
            {
                "name": "Groq",
                "url": "https://console.groq.com",
                "type": "LLM API",
                "cost": "免费额度充足，推理速度快",
                "priority": "high",
                "status": "pending_signup"
            },
            {
                "name": "Together AI",
                "url": "https://api.together.ai",
                "type": "开源模型",
                "cost": "免费试用，开源模型多",
                "priority": "mid",
                "status": "pending_signup"
            },
            {
                "name": "HuggingFace Inference",
                "url": "https://huggingface.co/inference",
                "type": "开源模型",
                "cost": "免费额度",
                "priority": "mid",
                "status": "available"
            }
        ]

        for resource in new_resources:
            print(f"发现: {resource['name']} - {resource['cost']}")
            # 可以扩展为自动注册或API调用

        return new_resources

    def analyze_efficiency(self):
        """分析效率指标"""
        print("\n📊 效率分析")
        print("=" * 50)

        # 检查任务看板
        task_board_file = self.workspace / "task-board.json"
        if task_board_file.exists():
            with open(task_board_file) as f:
                tasks = json.load(f)

            completed = sum(1 for t in tasks if t["status"] == "done")
            in_progress = sum(1 for t in tasks if t["status"] in ["progress", "in_progress"])

            print(f"已完成任务: {completed}")
            print(f"进行中任务: {in_progress}")
            print(f"完成率: {completed/(len(tasks))*100:.1f}%")

        # 建议优化点
        print("\n💡 优化建议:")
        print("1. 注册Groq获取免费额度")
        print("2. 充值Minimax ¥13")
        print("3. 优化API调用策略，减少token消耗")
        print("4. 自动化重复性任务")

        return {
            "completed": completed if 'completed' in dir() else 0,
            "in_progress": in_progress if 'in_progress' in dir() else 0
        }

    def generate商业_report(self):
        """生成商业化报告"""
        print("\n💼 商业化机会分析")
        print("=" * 50)

        # 基于现有工具识别商业化机会
        opportunities = [
            {
                "方向": "API代理服务",
                "描述": "利用多API切换能力，提供稳定的LLM调用服务",
                "成本": "低",
                "潜在收益": "中等",
                "难度": "低",
                "优先级": "高"
            },
            {
                "方向": "自动化工作流服务",
                "描述": "将自动化能力打包为企业服务",
                "成本": "中",
                "潜在收益": "高",
                "难度": "中",
                "优先级": "中"
            },
            {
                "方向": "技术咨询",
                "描述": "基于经验提供OpenClaw/AI工具咨询",
                "成本": "无",
                "潜在收益": "按项目",
                "难度": "低",
                "优先级": "高"
            }
        ]

        for i, opp in enumerate(opportunities, 1):
            print(f"\n{i}. {opp['方向']} (优先级: {opp['优先级']})")
            print(f"   描述: {opp['描述']}")
            print(f"   成本: {opp['成本']} | 收益: {opp['潜在收益']} | 难度: {opp['难度']}")

        self.opportunities = opportunities
        self.save_resources()

        return opportunities

    def run_full_optimization(self):
        """运行完整优化"""
        print(f"\n🚀 资源优化器启动 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)

        self.check_api_status()
        self.discover_new_resources()
        efficiency = self.analyze_efficiency()
        opportunities = self.generate商业_report()

        print("\n" + "=" * 60)
        print("✅ 优化完成!")

        # 保存效率指标
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "efficiency": efficiency,
            "api_count": len(self.api_resources),
            "opportunity_count": len(opportunities)
        }

        with open(self.efficiency_metrics_file, 'w') as f:
            json.dump(metrics, f, indent=2)

        return {
            "api_resources": self.api_resources,
            "efficiency": efficiency,
            "opportunities": opportunities
        }

if __name__ == "__main__":
    optimizer = ResourceOptimizer()
    optimizer.run_full_optimization()
