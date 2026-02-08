#!/usr/bin/env python3
"""
Skill Retriever v1.0 - 轻量级技能检索器
基于关键词匹配和标签系统，无需向量数据库
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Tuple
from dataclasses import dataclass

@dataclass
class SkillMatch:
    name: str
    description: str
    tags: List[str]
    score: float
    reason: str
    suggested_usage: str

class SkillRetriever:
    def __init__(self, skills_dir: str = None):
        # 尝试多个可能的路径
        if skills_dir:
            self.skills_dir = Path(skills_dir)
        else:
            # 默认路径：从脚本位置向上两级
            script_dir = Path(__file__).parent.parent.parent
            # 或者使用环境变量
            env_path = Path('/Users/fuzhuo/.openclaw/workspace/skills')
            
            if env_path.exists():
                self.skills_dir = env_path
            elif script_dir.exists():
                self.skills_dir = script_dir
            else:
                self.skills_dir = Path('.')
        
        self.skills_index = self._build_index()
        
        # 标签同义词映射
        self.tag_synonyms = {
            # 写作类
            'write': 'writing', 'writing': 'writing', 'create': 'writing',
            'text': 'writing', 'article': 'writing', 'essay': 'writing',
            'copy': 'marketing', 'copywriting': 'marketing', 'market': 'marketing',
            'sell': 'marketing', 'ad': 'marketing',
            'novel': 'fiction', 'story': 'fiction', 'fiction': 'fiction',
            
            # 分析类
            'analyze': 'analysis', 'analysis': 'analysis', 'research': 'research',
            'logic': 'logic', 'reasoning': 'logic', 'think': 'thinking',
            'data': 'data', 'statistics': 'data', 'chart': 'data',
            
            # 开发类
            'code': 'coding', 'coding': 'coding', 'program': 'coding',
            'develop': 'coding', 'script': 'scripting', 'automation': 'automation',
            'deploy': 'devops', 'docker': 'devops', 'ci': 'devops',
            'database': 'database', 'sql': 'database', 'query': 'database',
            'api': 'api', 'http': 'api', 'request': 'api',
            
            # 媒体类
            'image': 'image', 'photo': 'image', 'picture': 'image',
            'pdf': 'pdf', 'document': 'pdf', 'scan': 'pdf',
            'docx': 'docx', 'word': 'docx', 'ppt': 'pptx', 'excel': 'xlsx',
            'video': 'video', 'audio': 'audio',
            
            # 搜索类
            'search': 'search', 'find': 'search', 'lookup': 'search',
            'web': 'web', 'browser': 'web', 'scrape': 'web',
            'github': 'github', 'git': 'github', 'repo': 'github',
            
            # 思维类
            'brainstorm': 'brainstorm', 'idea': 'brainstorm',
            'decide': 'decision', 'decision': 'decision', 'choose': 'decision',
            'perspective': 'perspective', 'angle': 'perspective', 'view': 'perspective',
        }
    
    def _build_index(self) -> Dict:
        """构建技能索引"""
        index = {}
        skills_dir = self.skills_dir
        
        if not skills_dir.exists():
            return index
        
        for skill_dir in skills_dir.iterdir():
            if skill_dir.is_dir() and not skill_dir.name.startswith('.'):
                skill_file = skill_dir / 'SKILL.md'
                if skill_file.exists():
                    try:
                        with open(skill_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # 解析 frontmatter
                        name, description = self._parse_frontmatter(content)
                        
                        # 提取标签（从描述中推断）
                        tags = self._extract_tags(description, skill_dir.name)
                        
                        index[skill_dir.name] = {
                            'name': name or skill_dir.name,
                            'description': description,
                            'tags': tags,
                            'path': str(skill_dir)
                        }
                    except Exception as e:
                        print(f"Warning: Failed to parse {skill_dir.name}: {e}")
        
        return index
    
    def _parse_frontmatter(self, content: str) -> Tuple[str, str]:
        """解析YAML frontmatter"""
        name = ""
        description = ""
        
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                frontmatter = parts[1]
                # 提取 name
                name_match = re.search(r'^name:\s*(.+)$', frontmatter, re.MULTILINE)
                if name_match:
                    name = name_match.group(1).strip()
                # 提取 description
                desc_match = re.search(r'^description:\s*(.+)$', frontmatter, re.MULTILINE)
                if desc_match:
                    description = desc_match.group(1).strip()
        
        return name, description
    
    def _extract_tags(self, description: str, skill_name: str) -> List[str]:
        """从描述中提取标签"""
        tags = set()
        text = (description + ' ' + skill_name).lower()
        
        # 写作类
        if any(w in text for w in ['write', 'text', 'novel', 'story', '文学', '写作', '描写']):
            tags.add('writing')
        if any(w in text for w in ['market', 'sell', '宣传', '营销', '文案']):
            tags.add('marketing')
        if any(w in text for w in ['creative', '创意', '创作']):
            tags.add('creative')
        if any(w in text for w in ['fiction', 'novel', '小说']):
            tags.add('fiction')
        if any(w in text for w in ['academic', 'paper', '论文', '学术']):
            tags.add('academic')
            
        # 分析类
        if any(w in text for w in ['analyze', 'analysis', 'logic', '逻辑', '分析']):
            tags.add('analysis')
        if any(w in text for w in ['logic', 'reasoning', '推理', '逻辑']):
            tags.add('logic')
        if any(w in text for w in ['research', '研究', '调研']):
            tags.add('research')
        if any(w in text for w in ['data', '数据']):
            tags.add('data')
            
        # 开发类
        if any(w in text for w in ['code', 'coding', 'program', '开发', '代码']):
            tags.add('coding')
        if any(w in text for w in ['automation', 'automate', '自动', '脚本']):
            tags.add('automation')
        if any(w in text for w in ['database', 'sql', '数据库']):
            tags.add('database')
        if any(w in text for w in ['api', 'http', '接口']):
            tags.add('api')
        if any(w in text for w in ['devops', 'deploy', 'docker', '部署']):
            tags.add('devops')
        if any(w in text for w in ['script', '脚本']):
            tags.add('scripting')
            
        # 媒体类
        if any(w in text for w in ['image', 'picture', 'photo', '图片', '图像']):
            tags.add('image')
        if any(w in text for w in ['pdf', 'document', '文档']):
            tags.add('pdf')
        if any(w in text for w in ['docx', 'word', '文档']):
            tags.add('docx')
        if any(w in text for w in ['xlsx', 'excel', 'spreadsheet', '表格']):
            tags.add('xlsx')
        if any(w in text for w in ['pptx', 'ppt', 'presentation', '演示', '幻灯片']):
            tags.add('pptx')
        if any(w in text for w in ['video', '音频', '视频']):
            tags.add('media')
            
        # 搜索类
        if any(w in text for w in ['search', 'find', '搜索', '查找']):
            tags.add('search')
        if any(w in text for w in ['web', 'browser', 'scrape', '网页', '浏览器']):
            tags.add('web')
        if any(w in text for w in ['github', 'git', '仓库']):
            tags.add('github')
            
        # 思维类
        if any(w in text for w in ['brainstorm', 'idea', '头脑风暴', '创意']):
            tags.add('brainstorm')
        if any(w in text for w in ['decision', 'choose', '决策', '选择']):
            tags.add('decision')
        if any(w in text for w in ['thinking', 'think', '思维', '思考']):
            tags.add('thinking')
        if any(w in text for w in ['perspective', 'angle', 'view', '视角']):
            tags.add('perspective')
            
        return list(tags)
    
    def _extract_query_keywords(self, query: str) -> List[str]:
        """提取查询关键词 - 支持中英文"""
        query_lower = query.lower()
        
        # 中文分词：使用jieba或简单规则
        # 简单规则：提取连续的中文字符和英文单词
        import re
        
        # 提取英文单词
        english_words = re.findall(r'[a-zA-Z]+', query_lower)
        
        # 提取中文词（简单策略：去除常见停用词后保留）
        chinese_stopwords = {'我', '想', '要', '的', '了', '在', '有', '是', '和', '或', '用', '帮', '把', 
                           '请', '能', '处理', '一下', '这个', '那个', '帮我', '找', '个', '来', '去',
                           '一下', '看看', '有没有', '什么', '怎么', '如何', '可以', '需要'}
        
        # 移除停用词和短词
        keywords = []
        
        # 处理英文词
        for word in english_words:
            if len(word) > 1 and word not in {'am', 'is', 'are', 'the', 'a', 'an', 'in', 'on', 'at', 'to', 'for', 'of', 'and', 'or'}:
                keywords.append(word)
        
        # 处理中文：直接匹配关键技能词
        skill_keywords = {
            'pdf': 'pdf', '文档': 'pdf', '文件': 'pdf',
            'word': 'docx', 'docx': 'docx',
            'excel': 'xlsx', '表格': 'xlsx', 'xlsx': 'xlsx',
            'ppt': 'pptx', '幻灯片': 'pptx', '演示': 'pptx',
            '图片': 'image', '图像': 'image', 'photo': 'image', 'image': 'image',
            '写作': 'writing', '写': 'writing', '文字': 'writing', '文章': 'writing',
            '分析': 'analysis', '解析': 'analysis',
            '搜索': 'search', '查找': 'search', '查': 'search',
            '代码': 'coding', '编程': 'coding', '程序': 'coding',
            '自动化': 'automation', '自动': 'automation', '脚本': 'scripting',
            '数据库': 'database', '数据': 'data', 'sql': 'database',
            '逻辑': 'logic', '推理': 'logic',
            '视角': 'perspective', '角度': 'perspective',
            '细节': 'descriptive', '描写': 'descriptive', '画面': 'descriptive',
            '小说': 'fiction', '故事': 'fiction',
            '学术': 'academic', '论文': 'academic',
            '营销': 'marketing', '文案': 'marketing', '宣传': 'marketing',
            '问题': 'thinking', '思考': 'thinking', '思维': 'thinking',
            '清单': 'checklist', '列表': 'checklist',
            'github': 'github', 'git': 'github',
            '浏览器': 'web', '网页': 'web', '爬取': 'web',
            '视频': 'media', '音频': 'media',
        }
        
        for cn, tag in skill_keywords.items():
            if cn in query_lower:
                keywords.append(tag)
                keywords.append(cn)  # 同时保留原始中文词
        
        # 去重
        keywords = list(set(keywords))
        
        return keywords
    
    def _calculate_match_score(self, query: str, keywords: List[str], skill: Dict) -> Tuple[float, str]:
        """计算匹配分数"""
        name = skill['name'].lower()
        description = skill['description'].lower()
        tags = skill['tags']
        
        # 名称匹配 (40%)
        name_score = 0
        if any(kw in name for kw in keywords):
            name_score = sum(1 for kw in keywords if kw in name) / len(keywords)
            name_score = min(name_score * 1.5, 1.0)  # 名称匹配权重高
        
        # 描述匹配 (30%)
        desc_score = 0
        if any(kw in description for kw in keywords):
            desc_score = sum(1 for kw in keywords if kw in description) / len(keywords)
        
        # 标签匹配 (30%)
        tag_score = 0
        query_tags = set()
        for kw in keywords:
            if kw in self.tag_synonyms:
                query_tags.add(self.tag_synonyms[kw])
        
        if query_tags and tags:
            matched_tags = set(tags) & query_tags
            tag_score = len(matched_tags) / max(len(query_tags), 1)
        
        # 总分
        total_score = name_score * 0.4 + desc_score * 0.3 + tag_score * 0.3
        
        # 生成原因
        reasons = []
        if name_score > 0.5:
            reasons.append("名称匹配")
        if desc_score > 0.3:
            reasons.append("描述相关")
        if tag_score > 0.3:
            reasons.append("标签匹配")
        
        reason = "、".join(reasons) if reasons else "弱相关"
        
        return total_score, reason
    
    def _generate_suggested_usage(self, skill_name: str, query: str) -> str:
        """生成建议用法"""
        # 从查询中提取动作和对象
        patterns = [
            r'(?:用|使用)\s*(.+?)(?:来|去)?(.+)',
            r'(?:怎么|如何)(.+?)',
            r'(.+?)(?:相关的|有关的)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query)
            if match:
                action = match.group(1).strip()
                return f"用{skill_name}来{action}"
        
        return f"使用 {skill_name} 技能"
    
    def search(self, query: str, top_k: int = 5) -> List[SkillMatch]:
        """搜索技能"""
        keywords = self._extract_query_keywords(query)
        
        if not keywords:
            return []
        
        matches = []
        for skill_id, skill in self.skills_index.items():
            score, reason = self._calculate_match_score(query, keywords, skill)
            
            if score > 0.1:  # 阈值过滤
                matches.append(SkillMatch(
                    name=skill['name'],
                    description=skill['description'],
                    tags=skill['tags'],
                    score=score,
                    reason=reason,
                    suggested_usage=self._generate_suggested_usage(skill['name'], query)
                ))
        
        # 排序
        matches.sort(key=lambda x: x.score, reverse=True)
        
        return matches[:top_k]
    
    def search_by_tag(self, tag: str) -> List[SkillMatch]:
        """按标签搜索"""
        # 标准化标签
        normalized_tag = self.tag_synonyms.get(tag.lower(), tag.lower())
        
        matches = []
        for skill_id, skill in self.skills_index.items():
            if normalized_tag in skill['tags']:
                matches.append(SkillMatch(
                    name=skill['name'],
                    description=skill['description'],
                    tags=skill['tags'],
                    score=0.9,
                    reason=f"标签匹配: {normalized_tag}",
                    suggested_usage=f"使用 {skill['name']} 技能"
                ))
        
        return matches
    
    def list_all_skills(self) -> List[Dict]:
        """列出所有技能"""
        return [
            {
                'name': s['name'],
                'description': s['description'][:100] + '...' if len(s['description']) > 100 else s['description'],
                'tags': s['tags']
            }
            for s in self.skills_index.values()
        ]


def main():
    """CLI入口"""
    import sys
    
    retriever = SkillRetriever()
    
    if len(sys.argv) < 2:
        print("Usage: python skill_retriever.py <query>")
        print("       python skill_retriever.py --list")
        print("       python skill_retriever.py --tag <tag>")
        sys.exit(1)
    
    if sys.argv[1] == '--list':
        skills = retriever.list_all_skills()
        print(f"\n共 {len(skills)} 个技能：\n")
        for skill in sorted(skills, key=lambda x: x['name']):
            tags_str = ', '.join(skill['tags']) if skill['tags'] else '无标签'
            print(f"📦 {skill['name']}")
            print(f"   {skill['description']}")
            print(f"   标签: {tags_str}\n")
    
    elif sys.argv[1] == '--tag' and len(sys.argv) > 2:
        tag = sys.argv[2]
        matches = retriever.search_by_tag(tag)
        print(f"\n标签 '{tag}' 相关技能 ({len(matches)} 个)：\n")
        for match in matches:
            print(f"📦 {match.name}")
            print(f"   {match.description[:80]}...")
            print(f"   标签: {', '.join(match.tags)}\n")
    
    else:
        query = ' '.join(sys.argv[1:])
        matches = retriever.search(query)
        
        if not matches:
            print(f"\n未找到与 '{query}' 相关的技能")
            print("\n试试这些关键词：")
            print("  - 写作类: write, creative, text, novel")
            print("  - 分析类: analyze, logic, data, research")
            print("  - 开发类: code, api, database, automation")
            print("  - 搜索类: search, web, github")
            print("  - 媒体类: image, pdf, docx, video")
            sys.exit(0)
        
        print(f"\n找到 {len(matches)} 个相关技能：\n")
        
        for i, match in enumerate(matches, 1):
            score_pct = int(match.score * 100)
            icon = "🔥" if score_pct >= 80 else "📝" if score_pct >= 60 else "✨"
            
            print(f"{i}. {icon} {match.name} (匹配度: {score_pct}%)")
            print(f"   {match.description}")
            print(f"   标签: {', '.join(match.tags) if match.tags else '无'}")
            print(f"   原因: {match.reason}")
            print(f"   建议: \"{match.suggested_usage}\"\n")


if __name__ == '__main__':
    main()
