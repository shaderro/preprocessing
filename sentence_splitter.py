import re

def split_sentences(text):
    """
    将文本按句子分隔
    使用正则表达式匹配句号、问号、感叹号作为句子结束标记
    """
    # 使用正则表达式分割句子
    # 匹配句号、问号、感叹号，后面跟着空格或换行符
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    # 过滤掉空字符串并去除首尾空白
    sentences = [sentence.strip() for sentence in sentences if sentence.strip()]
    
    return sentences

def read_and_split_sentences(file_path):
    """
    读取txt文件并返回分割后的句子列表
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        sentences = split_sentences(content)
        return sentences
    
    except FileNotFoundError:
        print(f"错误：找不到文件 '{file_path}'")
        return []
    except Exception as e:
        print(f"读取文件时发生错误：{e}")
        return []

def main():
    # 测试文件路径
    test_file = "test_text.txt"
    
    print("正在读取文件并分割句子...")
    sentences = read_and_split_sentences(test_file)
    
    if sentences:
        print(f"\n共找到 {len(sentences)} 个句子：\n")
        for i, sentence in enumerate(sentences, 1):
            print(f"{i}. {sentence}")
    else:
        print("没有找到句子或文件读取失败")

if __name__ == "__main__":
    main() 