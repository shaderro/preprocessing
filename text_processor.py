#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import json
import os
import sys
from typing import List, Union, Dict, Any
from dataclasses import dataclass, asdict
from token_data import OriginalText, Sentence, Token

class TextProcessor:
    """文本处理器：将原始文本分割成结构化数据"""
    
    def __init__(self, output_base_dir: str = "data"):
        """
        初始化文本处理器
        
        Args:
            output_base_dir: 输出基础目录
        """
        self.output_base_dir = output_base_dir
        os.makedirs(output_base_dir, exist_ok=True)
    
    def split_sentences(self, text: str) -> List[str]:
        """
        将文本按句子分隔
        
        Args:
            text: 输入文本
            
        Returns:
            List[str]: 句子列表
        """
        # 使用正则表达式分割句子
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        # 过滤掉空字符串并去除首尾空白
        sentences = [sentence.strip() for sentence in sentences if sentence.strip()]
        
        return sentences
    
    def split_tokens(self, text: str) -> List[Dict[str, Any]]:
        """
        将文本分割成tokens
        
        Args:
            text: 输入文本
            
        Returns:
            List[Dict[str, Any]]: token列表
        """
        if not text:
            return []
        
        tokens = []
        
        # 使用正则表达式匹配不同类型的token
        word_pattern = r'\b[\w\'-]+\b'
        punctuation_pattern = r'[^\w\s]'
        space_pattern = r'\s+'
        
        # 组合所有模式
        combined_pattern = f'({word_pattern})|({punctuation_pattern})|({space_pattern})'
        
        matches = re.finditer(combined_pattern, text)
        
        for match in matches:
            token_body = match.group(0)
            
            # 确定token类型
            if match.group(1):  # 单词
                token_type = "text"
            elif match.group(2):  # 标点符号
                token_type = "punctuation"
            elif match.group(3):  # 空白字符
                token_type = "space"
            else:
                continue
            
            token = {
                "token_body": token_body,
                "token_type": token_type
            }
            
            tokens.append(token)
        
        return tokens
    
    def process_text_to_structured_data(self, text: Union[str, str], text_id: int, text_title: str = "") -> OriginalText:
        """
        将文本处理成结构化数据
        
        Args:
            text: 文本内容或文件路径
            text_id: 文本ID
            text_title: 文本标题
            
        Returns:
            OriginalText: 结构化的文本数据
        """
        # 如果输入是文件路径，先读取文件
        if os.path.isfile(text):
            with open(text, 'r', encoding='utf-8') as file:
                text_content = file.read()
            if not text_title:
                text_title = os.path.basename(text)
        else:
            text_content = text
            if not text_title:
                text_title = f"Text_{text_id}"
        
        # 分割句子
        sentence_texts = self.split_sentences(text_content)
        
        # 创建句子对象列表
        sentences = []
        global_token_id = 0
        
        for sentence_id, sentence_text in enumerate(sentence_texts, 1):
            # 分割tokens
            token_dicts = self.split_tokens(sentence_text)
            
            # 创建Token对象列表
            tokens = []
            for token_id, token_dict in enumerate(token_dicts, 1):
                token = Token(
                    token_body=token_dict["token_body"],
                    token_type=token_dict["token_type"],
                    global_token_id=global_token_id,
                    sentence_token_id=token_id
                )
                tokens.append(token)
                global_token_id += 1
            
            # 创建Sentence对象
            sentence = Sentence(
                text_id=text_id,
                sentence_id=sentence_id,
                sentence_body=sentence_text,
                grammar_annotations=[],
                vocab_annotations=[],
                tokens=tokens
            )
            sentences.append(sentence)
        
        # 创建OriginalText对象
        original_text = OriginalText(
            text_id=text_id,
            text_title=text_title,
            text_by_sentence=sentences
        )
        
        return original_text
    
    def save_structured_data(self, original_text: OriginalText, output_dir: str):
        """
        保存结构化数据到指定目录（优化版本，避免重复冗余）
        
        Args:
            original_text: 结构化的文本数据
            output_dir: 输出目录路径
        """
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 1. 保存 original_texts.json（只保留整体文本和 metadata）
        original_text_data = {
            "text_id": original_text.text_id,
            "text_title": original_text.text_title,
            "text_body": "\n".join([sentence.sentence_body for sentence in original_text.text_by_sentence]),
            "sentence_ids": [sentence.sentence_id for sentence in original_text.text_by_sentence]
        }
        
        with open(os.path.join(output_dir, "original_texts.json"), 'w', encoding='utf-8') as f:
            json.dump(original_text_data, f, ensure_ascii=False, indent=2)
        
        # 2. 保存 sentences.json（按 sentence 拆分，避免重复 text_id）
        sentences_data = []
        for sentence in original_text.text_by_sentence:
            # 收集该句子的所有token IDs
            token_ids = [token.global_token_id for token in sentence.tokens]
            
            sentence_data = {
                "sentence_id": sentence.sentence_id,
                "text_id": sentence.text_id,
                "sentence_body": sentence.sentence_body,
                "token_ids": token_ids,
                "grammar_annotations": sentence.grammar_annotations,
                "vocab_annotations": sentence.vocab_annotations
            }
            sentences_data.append(sentence_data)
        
        with open(os.path.join(output_dir, "sentences.json"), 'w', encoding='utf-8') as f:
            json.dump(sentences_data, f, ensure_ascii=False, indent=2)
        
        # 3. 保存 tokens.json（独立保存所有 token 信息，提供全局索引）
        all_tokens = []
        for sentence in original_text.text_by_sentence:
            for token_index, token in enumerate(sentence.tokens):
                token_data = {
                    "token_id": token.global_token_id,
                    "sentence_id": sentence.sentence_id,
                    "token_body": token.token_body,
                    "token_type": token.token_type,
                    "sentence_token_index": token_index,
                    "difficulty_level": token.difficulty_level,
                    "explanation": token.explanation,
                    "pos_tag": token.pos_tag,
                    "lemma": token.lemma,
                    "is_grammar_marker": token.is_grammar_marker
                }
                all_tokens.append(token_data)
        
        with open(os.path.join(output_dir, "tokens.json"), 'w', encoding='utf-8') as f:
            json.dump(all_tokens, f, ensure_ascii=False, indent=2)
    
    def process_file(self, input_path: str, text_id: int, output_dir: str = None) -> bool:
        """
        处理文本文件并保存结构化数据
        
        Args:
            input_path: 输入文件路径
            text_id: 文本ID
            output_dir: 输出目录路径，如果为None则使用默认路径
            
        Returns:
            bool: 处理是否成功
        """
        try:
            if output_dir is None:
                output_dir = os.path.join(self.output_base_dir, f"text_{text_id:03d}")
            
            # 检查输入文件是否存在
            if not os.path.exists(input_path):
                print(f"❌ 错误：找不到文件 '{input_path}'")
                return False
            
            # 处理文本
            original_text = self.process_text_to_structured_data(input_path, text_id)
            
            # 保存数据
            self.save_structured_data(original_text, output_dir)
            
            print(f"✅ 文本处理完成！")
            print(f"📁 输出目录: {output_dir}")
            print(f"📄 句子数量: {len(original_text.text_by_sentence)}")
            print(f"🔤 总token数量: {sum(len(sentence.tokens) for sentence in original_text.text_by_sentence)}")
            
            return True
            
        except Exception as e:
            print(f"❌ 处理文件时发生错误：{e}")
            return False
    
    def process_multiple_files(self, input_files: List[str], start_text_id: int = 1) -> int:
        """
        批量处理多个文件
        
        Args:
            input_files: 输入文件路径列表
            start_text_id: 起始文本ID
            
        Returns:
            int: 成功处理的文件数量
        """
        success_count = 0
        
        print(f"🔄 开始批量处理 {len(input_files)} 个文件...")
        print("=" * 50)
        
        for i, file_path in enumerate(input_files, start_text_id):
            print(f"\n📝 处理文件 {i-start_text_id+1}/{len(input_files)}: {file_path}")
            
            if self.process_file(file_path, i):
                success_count += 1
            else:
                print(f"⚠️  跳过文件: {file_path}")
        
        print(f"\n📊 批量处理完成！成功处理 {success_count}/{len(input_files)} 个文件")
        return success_count

def main():
    """主函数：处理命令行输入的文件"""
    
    # 检查命令行参数
    if len(sys.argv) < 2:
        print("使用方法: python text_processor.py <文件路径1> [文件路径2] [文件路径3] ...")
        print("示例: python text_processor.py input.txt")
        print("示例: python text_processor.py file1.txt file2.txt file3.txt")
        sys.exit(1)
    
    # 获取文件路径列表
    input_files = sys.argv[1:]
    
    # 创建文本处理器
    processor = TextProcessor()
    
    # 处理文件
    if len(input_files) == 1:
        # 单个文件处理
        success = processor.process_file(input_files[0], 1)
        if not success:
            sys.exit(1)
    else:
        # 批量处理
        success_count = processor.process_multiple_files(input_files)
        if success_count == 0:
            sys.exit(1)

if __name__ == "__main__":
    main() 