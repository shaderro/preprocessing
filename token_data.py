from typing import Optional, Literal
from dataclasses import dataclass


@dataclass
class Sentence:
    text_id: int
    sentence_id: int
    sentence_body: str
    grammar_annotations: list[int] #rule id
    vocab_annotations: list[int] #word id

@dataclass
class OriginalText:
    text_id: int
    text_title: str
    text_by_sentence: list[Sentence]

class Token:
    token_body: str
    token_type: Literal["text", "punctuation", "space"]
    difficulty_level: Optional[Literal["easy", "hard"]] = None
    explanation: Optional[str] = None
    pos_tag: Optional[str] = None              # 词性标注（可选：用于后续语法分析）
    lemma: Optional[str] = None                # 原型词（用于合并变形、统一解释）
    is_grammar_marker: Optional[bool] = False  # 是否参与语法结构识别

"""
 {
  "token_body": "Although",
  "token_type": "text",
  "difficulty_level": "hard",
  "explanation": "Used to introduce a contrast clause.",
  "pos_tag": "SCONJ",
  "lemma": "although",
  "is_grammar_marker": true
}"""