"""
Evaluation utilities for AI API conversations.
"""
import os
import json
import time
import numpy as np
from typing import List, Dict, Any, Optional

# 评分维度和权重
EVALUATION_DIMENSIONS = {
    "relevance": {
        "description": "回答与问题的相关性",
        "weight": 0.25
    },
    "accuracy": {
        "description": "回答的准确性和正确性",
        "weight": 0.25
    },
    "completeness": {
        "description": "回答的完整性和全面性",
        "weight": 0.20
    },
    "coherence": {
        "description": "回答的连贯性和逻辑性",
        "weight": 0.15
    },
    "creativity": {
        "description": "回答的创新性和独特性",
        "weight": 0.15
    }
}

class ConversationEvaluator:
    """评估对话质量的评估器"""
    
    def __init__(self, dimensions=None):
        """
        初始化评估器
        
        Args:
            dimensions: 评分维度和权重，默认使用EVALUATION_DIMENSIONS
        """
        self.dimensions = dimensions or EVALUATION_DIMENSIONS
        
    def evaluate_response(self, prompt, response, context=None):
        """
        评估单个回复的质量
        
        Args:
            prompt: 用户提问
            response: API回复
            context: 对话上下文（可选）
            
        Returns:
            评分结果字典
        """
        # 这里使用简单的启发式规则进行评分
        scores = {}
        
        # 相关性评分
        scores["relevance"] = self._evaluate_relevance(prompt, response)
        
        # 准确性评分
        scores["accuracy"] = self._evaluate_accuracy(prompt, response)
        
        # 完整性评分
        scores["completeness"] = self._evaluate_completeness(prompt, response)
        
        # 连贯性评分
        scores["coherence"] = self._evaluate_coherence(prompt, response, context)
        
        # 创新性评分
        scores["creativity"] = self._evaluate_creativity(response)
        
        # 计算加权总分
        total_score = 0
        for dim, score in scores.items():
            total_score += score * self.dimensions[dim]["weight"]
        
        return {
            "dimensions": {dim: {"score": score, "weight": self.dimensions[dim]["weight"]} 
                          for dim, score in scores.items()},
            "total_score": total_score
        }
    
    def evaluate_conversation(self, conversation):
        """
        评估整个对话的质量
        
        Args:
            conversation: 对话对象
            
        Returns:
            评分结果字典
        """
        scores = []
        context = []
        
        # 评估每一轮对话
        for i in range(0, len(conversation.messages), 2):
            if i+1 < len(conversation.messages):
                prompt = conversation.messages[i]["content"] if isinstance(conversation.messages[i], dict) else conversation.messages[i].content
                response = conversation.messages[i+1]["content"] if isinstance(conversation.messages[i+1], dict) else conversation.messages[i+1].content
                
                # 如果不是字符串，尝试提取文本内容
                if not isinstance(prompt, str):
                    if isinstance(prompt, list):
                        prompt_texts = []
                        for item in prompt:
                            if isinstance(item, dict) and "text" in item:
                                prompt_texts.append(item["text"])
                        prompt = " ".join(prompt_texts)
                    elif isinstance(prompt, dict) and "text" in prompt:
                        prompt = prompt["text"]
                    else:
                        prompt = str(prompt)
                
                # 评估当前回复
                score = self.evaluate_response(prompt, response, context)
                scores.append(score)
                
                # 更新上下文
                context.append({"prompt": prompt, "response": response})
        
        # 计算平均分
        if scores:
            avg_total = sum(score["total_score"] for score in scores) / len(scores)
            avg_dimensions = {}
            for dim in self.dimensions:
                avg_dimensions[dim] = sum(score["dimensions"][dim]["score"] for score in scores) / len(scores)
            
            return {
                "turn_scores": scores,
                "average_score": avg_total,
                "average_dimensions": avg_dimensions
            }
        else:
            return {"error": "No valid turns to evaluate"}
    
    def _evaluate_relevance(self, prompt, response):
        """评估回复与问题的相关性"""
        # 简单启发式：检查问题中的关键词是否出现在回复中
        prompt_words = set(self._tokenize(prompt.lower()))
        response_words = set(self._tokenize(response.lower()))
        
        # 计算关键词重叠率
        overlap = len(prompt_words.intersection(response_words)) / max(1, len(prompt_words))
        
        # 回复长度因子（过长或过短的回复可能不太相关）
        length_factor = min(1.0, len(response) / 1000) * min(1.0, 5000 / max(1, len(response)))
        
        # 综合评分
        score = 0.7 + (0.3 * overlap * length_factor)
        return min(1.0, max(0.0, score))
    
    def _evaluate_accuracy(self, prompt, response):
        """评估回复的准确性"""
        # 由于无法直接判断准确性，这里使用启发式规则
        
        # 检查是否包含不确定性表达
        uncertainty_phrases = ["我不确定", "可能", "也许", "我猜", "不太清楚", "不太确定"]
        uncertainty_count = sum(phrase in response.lower() for phrase in uncertainty_phrases)
        
        # 检查是否包含事实性表述
        fact_indicators = ["事实上", "研究表明", "数据显示", "根据", "证明", "证实"]
        fact_count = sum(indicator in response.lower() for indicator in fact_indicators)
        
        # 基础分
        base_score = 0.8
        
        # 调整分数
        score = base_score - (uncertainty_count * 0.05) + (fact_count * 0.03)
        return min(1.0, max(0.5, score))  # 准确性最低给0.5分
    
    def _evaluate_completeness(self, prompt, response):
        """评估回复的完整性"""
        # 回复长度因子
        length_score = min(1.0, len(response) / 500)
        
        # 检查是否包含结构化内容（如列表、小标题等）
        structure_indicators = ["：", ":", "\n-", "\n•", "\n*", "\n1.", "首先", "其次", "最后", "总结"]
        has_structure = any(indicator in response for indicator in structure_indicators)
        structure_score = 0.2 if has_structure else 0
        
        # 综合评分
        score = 0.7 * length_score + 0.3 + structure_score
        return min(1.0, score)
    
    def _evaluate_coherence(self, prompt, response, context):
        """评估回复的连贯性"""
        # 基础分
        base_score = 0.8
        
        # 检查段落结构
        paragraphs = response.split("\n\n")
        paragraph_score = min(1.0, len(paragraphs) / 3) * 0.1
        
        # 检查逻辑连接词
        connectors = ["因此", "所以", "然而", "但是", "此外", "另外", "总之", "首先", "其次", "最后"]
        connector_count = sum(connector in response.lower() for connector in connectors)
        connector_score = min(0.1, connector_count * 0.02)
        
        # 上下文连贯性（如果有上下文）
        context_score = 0
        if context:
            # 检查是否引用了之前的对话内容
            prev_responses = " ".join([c["response"] for c in context])
            prev_prompts = " ".join([c["prompt"] for c in context])
            
            prev_words = set(self._tokenize((prev_responses + " " + prev_prompts).lower()))
            response_words = set(self._tokenize(response.lower()))
            
            context_overlap = len(prev_words.intersection(response_words)) / max(1, len(response_words))
            context_score = context_overlap * 0.1
        
        # 综合评分
        score = base_score + paragraph_score + connector_score + context_score
        return min(1.0, score)
    
    def _evaluate_creativity(self, response):
        """评估回复的创新性"""
        # 检查是否包含比喻、类比等修辞手法
        rhetoric_phrases = ["就像", "类似于", "可以比作", "想象", "比如说", "形象地说"]
        rhetoric_count = sum(phrase in response.lower() for phrase in rhetoric_phrases)
        
        # 检查词汇多样性
        words = self._tokenize(response.lower())
        unique_words = set(words)
        vocabulary_diversity = len(unique_words) / max(1, len(words))
        
        # 检查句式多样性
        sentences = [s.strip() for s in response.replace("！", "。").replace("？", "。").replace("!", ".").replace("?", ".").split("。") if s.strip()]
        sentence_lengths = [len(s) for s in sentences]
        sentence_diversity = np.std(sentence_lengths) / max(1, np.mean(sentence_lengths)) if sentences else 0
        
        # 综合评分
        base_score = 0.7
        rhetoric_score = min(0.1, rhetoric_count * 0.03)
        diversity_score = vocabulary_diversity * 0.1
        sentence_score = min(0.1, sentence_diversity * 0.5)
        
        score = base_score + rhetoric_score + diversity_score + sentence_score
        return min(1.0, max(0.5, score))  # 创新性最低给0.5分
    
    def _tokenize(self, text):
        """简单分词"""
        # 这里使用简单的空格分词，实际应用中可以使用更复杂的分词器
        return text.replace("，", " ").replace("。", " ").replace("！", " ").replace("？", " ").replace("、", " ").split()


def evaluate_api_responses(results_file):
    """
    评估API响应结果文件中的所有对话
    
    Args:
        results_file: 结果文件路径
        
    Returns:
        评分结果字典
    """
    try:
        with open(results_file, 'r', encoding='utf-8') as f:
            results = json.load(f)
    except Exception as e:
        return {"error": f"Failed to load results file: {str(e)}"}
    
    evaluator = ConversationEvaluator()
    evaluation_results = {}
    
    # 遍历每个对话流程
    for flow_id, flow_data in results.items():
        test_evaluation = {}
        
        # 获取对话流程信息
        name = flow_data.get('name', '')
        description = flow_data.get('description', '')
        
        # 遍历每个API的结果
        for api_name, api_result in flow_data.get('api_results', {}).items():
            # 获取对话ID
            conversation_id = api_result.get('conversation_id')
            if not conversation_id:
                continue
                
            # 读取对话文件
            conv_file = None
            for root, dirs, files in os.walk('conversations'):
                for file in files:
                    if conversation_id in file and api_name in file:
                        conv_file = os.path.join(root, file)
                        break
                if conv_file:
                    break
            
            if not conv_file:
                test_evaluation[api_name] = {"error": "Conversation file not found"}
                continue
                
            try:
                with open(conv_file, 'r', encoding='utf-8') as f:
                    conversation_data = json.load(f)
                    
                # 创建简单的Conversation对象用于评估
                class SimpleConversation:
                    def __init__(self, data):
                        self.messages = data.get('messages', [])
                        
                conversation = SimpleConversation(conversation_data)
                
                # 评估对话
                evaluation = evaluator.evaluate_conversation(conversation)
                test_evaluation[api_name] = evaluation
                
            except Exception as e:
                test_evaluation[api_name] = {"error": f"Evaluation failed: {str(e)}"}
        
        evaluation_results[flow_id] = {
            "name": name,
            "description": description,
            "api_evaluations": test_evaluation
        }
    
    # 计算每个API的总体评分
    api_overall_scores = {}
    for test_case_id, test_eval in evaluation_results.items():
        for api_name, api_eval in test_eval.get('api_evaluations', {}).items():
            if "error" in api_eval:
                continue
                
            if api_name not in api_overall_scores:
                api_overall_scores[api_name] = []
                
            api_overall_scores[api_name].append(api_eval.get('average_score', 0))
    
    # 计算平均分
    for api_name, scores in api_overall_scores.items():
        if scores:
            api_overall_scores[api_name] = sum(scores) / len(scores)
        else:
            api_overall_scores[api_name] = 0
    
    # 添加总体评分到结果中
    evaluation_results["overall_scores"] = api_overall_scores
    
    # 保存评估结果
    os.makedirs('evaluations', exist_ok=True)
    output_file = f"evaluations/evaluation_results_{int(time.time())}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(evaluation_results, f, indent=2, ensure_ascii=False)
    
    print(f"\nEvaluation results saved to {output_file}")
    return evaluation_results
