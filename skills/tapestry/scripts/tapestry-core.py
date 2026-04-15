#!/usr/bin/env python3
"""
tapestry-core.py - 知识图谱构建核心脚本

功能：
- 文档解析（文本、PDF、Markdown）
- 实体提取（使用 spaCy 或正则表达式）
- 关系建立（文档间、实体间关联）
- 知识检索（基于图的查询）
- 可视化数据导出
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict

# 尝试导入可选依赖
try:
    import networkx as nx
except ImportError:
    nx = None

try:
    import spacy
except ImportError:
    spacy = None

try:
    from PyPDF2 import PdfReader
except ImportError:
    PdfReader = None


class KnowledgeGraph:
    """知识图谱管理类"""
    
    def __init__(self, storage_dir: str = "data"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # 图结构
        self.graph = nx.Graph() if nx else None
        
        # 数据存储
        self.entities: Dict[str, Dict] = {}
        self.documents: Dict[str, Dict] = {}
        self.relations: List[Dict] = []
        
        # 加载已有数据
        self._load_data()
    
    def _load_data(self):
        """加载已有数据"""
        entities_file = self.storage_dir / "entities.json"
        documents_file = self.storage_dir / "documents.json"
        relations_file = self.storage_dir / "relations.json"
        
        if entities_file.exists():
            with open(entities_file, 'r', encoding='utf-8') as f:
                self.entities = json.load(f)
        
        if documents_file.exists():
            with open(documents_file, 'r', encoding='utf-8') as f:
                self.documents = json.load(f)
        
        if relations_file.exists():
            with open(relations_file, 'r', encoding='utf-8') as f:
                self.relations = json.load(f)
        
        if self.graph and self.relations:
            for rel in self.relations:
                self.graph.add_edge(rel.get('source', ''), rel.get('target', ''), 
                                   relation=rel.get('type', ''))
    
    def _save_data(self):
        """保存数据"""
        entities_file = self.storage_dir / "entities.json"
        documents_file = self.storage_dir / "documents.json"
        relations_file = self.storage_dir / "relations.json"
        
        with open(entities_file, 'w', encoding='utf-8') as f:
            json.dump(self.entities, f, ensure_ascii=False, indent=2)
        
        with open(documents_file, 'w', encoding='utf-8') as f:
            json.dump(self.documents, f, ensure_ascii=False, indent=2)
        
        with open(relations_file, 'w', encoding='utf-8') as f:
            json.dump(self.relations, f, ensure_ascii=False, indent=2)
    
    def add_document(self, doc_id: str, content: str, metadata: Dict = None):
        """添加文档"""
        self.documents[doc_id] = {
            "content": content,
            "metadata": metadata or {},
            "entities": [],
            "created_at": self._timestamp()
        }
        return doc_id
    
    def extract_entities(self, text: str, method: str = "regex") -> List[Dict]:
        """提取实体"""
        entities = []
        
        if method == "spacy" and spacy:
            entities = self._extract_entities_spacy(text)
        else:
            entities = self._extract_entities_regex(text)
        
        # 去重
        seen = set()
        unique_entities = []
        for e in entities:
            key = (e["text"], e["type"])
            if key not in seen:
                seen.add(key)
                unique_entities.append(e)
        
        return unique_entities
    
    def _extract_entities_spacy(self, text: str) -> List[Dict]:
        """使用 spaCy 提取实体"""
        if not spacy:
            return self._extract_entities_regex(text)
        
        try:
            nlp = spacy.load("zh_core_web_sm")
            doc = nlp(text)
            
            entities = []
            for ent in doc.ents:
                entities.append({
                    "text": ent.text,
                    "type": ent.label_,
                    "start": ent.start_char,
                    "end": ent.end_char
                })
            return entities
        except OSError:
            print("Warning: spaCy model not found, using regex")
            return self._extract_entities_regex(text)
    
    def _extract_entities_regex(self, text: str) -> List[Dict]:
        """使用正则表达式提取实体"""
        entities = []
        
        # 中文人名模式（简化）
        name_pattern = re.compile(r'[王李张刘陈杨赵黄周吴徐孙马胡郭何高林罗郑梁谢宋唐许邓冯韩曹曾彭萧蔡潘田董袁于余叶蒋杜苏魏程吕丁沈任姚卢傅钟姜崔谭陆汪范金石廖贾夏韦傅方孟邱贺白秦孔')
        name_matches = re.findall(r'[王李张刘陈杨赵黄周吴徐孙马胡郭何高林罗郑梁谢宋唐许邓冯韩曹曾彭萧蔡潘田董袁于余叶蒋杜苏魏程吕丁沈任姚卢傅钟姜崔谭陆汪范金石廖贾夏韦傅方孟邱贺白秦孔]{1,2}', text)
        for name in set(name_matches):
            if len(name) >= 2:
                entities.append({"text": name, "type": "PERSON", "confidence": 0.8})
        
        # 组织机构模式
        org_patterns = [
            r'(公司|集团|大学|学院|医院|银行|政府|局|部|处|室|中心|协会|基金会)',
        ]
        for pattern in org_patterns:
            matches = re.findall(pattern, text)
            for match in set(matches):
                entities.append({"text": match, "type": "ORG", "confidence": 0.7})
        
        # 地名模式
        location_patterns = [
            r'(北京|上海|广州|深圳|杭州|南京|武汉|成都|西安|重庆|天津)',
        ]
        for pattern in location_patterns:
            matches = re.findall(pattern, text)
            for match in set(matches):
                entities.append({"text": match, "type": "GPE", "confidence": 0.9})
        
        return entities
    
    def add_entities_to_document(self, doc_id: str, entities: List[Dict]):
        """将实体添加到文档"""
        if doc_id not in self.documents:
            raise ValueError(f"Document {doc_id} not found")
        
        self.documents[doc_id]["entities"] = entities
        
        # 更新全局实体库
        for entity in entities:
            entity_key = entity["text"]
            if entity_key not in self.entities:
                self.entities[entity_key] = {
                    "text": entity_key,
                    "type": entity.get("type", "UNKNOWN"),
                    "documents": [],
                    "count": 0
                }
            if doc_id not in self.entities[entity_key]["documents"]:
                self.entities[entity_key]["documents"].append(doc_id)
            self.entities[entity_key]["count"] += 1
    
    def add_relation(self, source: str, target: str, relation_type: str, metadata: Dict = None):
        """添加关系"""
        relation = {
            "source": source,
            "target": target,
            "type": relation_type,
            "metadata": metadata or {}
        }
        self.relations.append(relation)
        
        if self.graph:
            self.graph.add_edge(source, target, relation=relation_type)
        
        return relation
    
    def find_relations(self, entity: str, max_depth: int = 2) -> List[Dict]:
        """查找与实体相关的关系"""
        results = []
        
        for rel in self.relations:
            if rel["source"] == entity or rel["target"] == entity:
                results.append(rel)
        
        return results
    
    def graph_search(self, query_entity: str, depth: int = 2) -> List[Tuple]:
        """图结构搜索"""
        if not self.graph:
            raise RuntimeError("networkx not available")
        
        results = []
        try:
            # 查找直接连接的节点
            neighbors = list(self.graph.neighbors(query_entity))
            results.append((query_entity, neighbors, 1))
            
            # 广度优先搜索
            for i in range(2, depth + 1):
                level_nodes = []
                for node in results[-1][1]:
                    level_nodes.extend(list(self.graph.neighbors(node)))
                results.append((query_entity, list(set(level_nodes)), i))
        except nx.NetworkXError:
            pass
        
        return results
    
    def export_graph(self, format: str = "json") -> Dict:
        """导出图数据"""
        if format == "json":
            return {
                "nodes": [
                    {"id": e["text"], "label": e["text"], "type": e["type"]}
                    for e in self.entities.values()
                ],
                "edges": [
                    {"source": r["source"], "target": r["target"], "type": r["type"]}
                    for r in self.relations
                ],
                "statistics": {
                    "entity_count": len(self.entities),
                    "relation_count": len(self.relations),
                    "document_count": len(self.documents)
                }
            }
        
        elif format == "gexf":
            # GEXF 格式（用于 Gephi 等工具）
            nodes = []
            for i, e in enumerate(self.entities.values()):
                nodes.append(f'  <node id="{e["text"]}" label="{e["text"]}" type="{e["type"]}"/>')
            
            edges = []
            for i, r in enumerate(self.relations):
                edges.append(f'  <edge id="{i}" source="{r["source"]}" target="{r["target"]}" type="{r["type"]}"/>')
            
            return {
                "content": f'''<?xml version="1.0" encoding="UTF-8"?>
<gexf xmlns="http://www.gexf.net/1.2draft" version="1.2">
  <graph mode="static" defaultedgetype="undirected">
    <nodes>
{chr(10).join(nodes)}
    </nodes>
    <edges>
{chr(10).join(edges)}
    </edges>
  </graph>
</gexf>'''
            }
        
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _timestamp(self) -> str:
        """生成时间戳"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def save(self):
        """保存图谱"""
        self._save_data()


class DocumentParser:
    """文档解析器"""
    
    @staticmethod
    def parse(file_path: str) -> Tuple[str, str, Dict]:
        """解析文档"""
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        extension = path.suffix.lower()
        
        if extension in ['.txt', '.md']:
            return DocumentParser._parse_text(path)
        elif extension == '.pdf':
            return DocumentParser._parse_pdf(path)
        else:
            raise ValueError(f"Unsupported format: {extension}")
    
    @staticmethod
    def _parse_text(path: Path) -> Tuple[str, str, Dict]:
        """解析文本文件"""
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        metadata = {
            "file_name": path.name,
            "file_path": str(path),
            "file_size": path.stat().st_size,
            "format": path.suffix.lstrip('.').upper()
        }
        
        return path.stem, content, metadata
    
    @staticmethod
    def _parse_pdf(path: Path) -> Tuple[str, str, Dict]:
        """解析 PDF 文件"""
        if not PdfReader:
            raise RuntimeError("PyPDF2 not installed")
        
        reader = PdfReader(path)
        text_parts = []
        
        for page in reader.pages:
            text = page.extract_text()
            if text:
                text_parts.append(text)
        
        content = "\n".join(text_parts)
        
        metadata = {
            "file_name": path.name,
            "file_path": str(path),
            "file_size": path.stat().st_size,
            "format": "PDF",
            "page_count": len(reader.pages)
        }
        
        return path.stem, content, metadata


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(description="tapestry - 知识图谱构建工具")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # parse 命令
    parse_parser = subparsers.add_parser("parse", help="解析文档")
    parse_parser.add_argument("--input", "-i", required=True, help="输入文件路径")
    parse_parser.add_argument("--format", "-f", default="auto", help="文件格式 (auto, text, pdf, md)")
    
    # extract 命令
    extract_parser = subparsers.add_parser("extract", help="提取实体")
    extract_parser.add_argument("--text", "-t", required=True, help="要处理的文本")
    extract_parser.add_argument("--method", "-m", default="regex", help="提取方法 (regex, spacy)")
    
    # relate 命令
    relate_parser = subparsers.add_parser("relate", help="建立关系")
    relate_parser.add_argument("--doc1", required=True, help="文档1 ID")
    relate_parser.add_argument("--doc2", required=True, help="文档2 ID")
    relate_parser.add_argument("--type", "-t", default="related", help="关系类型")
    
    # query 命令
    query_parser = subparsers.add_parser("query", help="查询知识")
    query_parser.add_argument("--entity", "-e", required=True, help="查询实体")
    query_parser.add_argument("--depth", "-d", default=2, type=int, help="查询深度")
    
    # export 命令
    export_parser = subparsers.add_parser("export", help="导出图数据")
    export_parser.add_argument("--format", "-f", default="json", help="导出格式 (json, gexf)")
    export_parser.add_argument("--output", "-o", default="graph_export", help="输出文件前缀")
    
    # stats 命令
    stats_parser = subparsers.add_parser("stats", help="显示统计信息")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # 初始化知识图谱
    kg = KnowledgeGraph()
    
    if args.command == "parse":
        try:
            doc_id, content, metadata = DocumentParser.parse(args.input)
            kg.add_document(doc_id, content, metadata)
            print(f"✓ Document parsed: {doc_id}")
            
            # 提取实体
            entities = kg.extract_entities(content)
            kg.add_entities_to_document(doc_id, entities)
            print(f"✓ Extracted {len(entities)} entities")
            
            kg.save()
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
    
    elif args.command == "extract":
        try:
            entities = kg.extract_entities(args.text, args.method)
            print(json.dumps(entities, ensure_ascii=False, indent=2))
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
    
    elif args.command == "relate":
        try:
            kg.add_relation(args.doc1, args.doc2, args.type)
            kg.save()
            print(f"✓ Relation added: {args.doc1} --{args.type}--> {args.doc2}")
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
    
    elif args.command == "query":
        try:
            if nx:
                results = kg.graph_search(args.entity, args.depth)
                for level, nodes, depth in results:
                    print(f"Depth {depth}: {nodes}")
            else:
                relations = kg.find_relations(args.entity)
                print(json.dumps(relations, ensure_ascii=False, indent=2))
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
    
    elif args.command == "export":
        try:
            export_data = kg.export_graph(args.format)
            
            if args.format == "json":
                output_file = f"{args.output}.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, ensure_ascii=False, indent=2)
                print(f"✓ Exported to {output_file}")
            elif args.format == "gexf":
                output_file = f"{args.output}.gexf"
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(export_data["content"])
                print(f"✓ Exported to {output_file}")
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
    
    elif args.command == "stats":
        stats = {
            "documents": len(kg.documents),
            "entities": len(kg.entities),
            "relations": len(kg.relations)
        }
        print(json.dumps(stats, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
