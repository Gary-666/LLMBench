# LLMBench

*[English](#english-version) | [中文](#chinese-version)*

---

<a id="english-version"></a>
## English Version

AIBench is a powerful AI model evaluation framework designed to compare and test the conversational capabilities of different large language model APIs. Through standardized test scenarios and a precise scoring system, AIBench helps you objectively evaluate the performance of various AI models.

### ✨ Key Features

- **Multi-API Support**: Test and compare multiple AI APIs simultaneously (Monica, OpenAI, Gemini, etc.)
- **Multi-turn Conversation Evaluation**: Test AI performance in complex conversation flows
- **Comprehensive Scoring System**: Score based on relevance, accuracy, completeness, coherence, and creativity
- **Flexible Model Configuration**: Easily configure the models used by each API through environment variables
- **Rich Test Scenarios**: Preset various test scenarios covering basic Q&A, creative generation, logical reasoning, etc.
- **Detailed Evaluation Reports**: Generate comprehensive evaluation reports for intuitive comparison of different API performance

### 🚀 Quick Start

#### Installation

```bash
# Clone the repository
git clone https://github.com/Gary-666/LLMBench.git
cd LLMBench

# Install dependencies
pip install -r requirements.txt
```

#### Configuration

Create a `.env` file and add your API keys and model configurations:

```
# API Keys
MONICA_KEY=your_monica_api_key
OPENAI_API_KEY=your_openai_api_key
GEMINI_KEY=your_gemini_api_key

# Model Configurations
MONICA_MODEL=gpt-4o
OPENAI_TEXT_MODEL=gpt-4.1
OPENAI_VISION_MODEL=gpt-4.1
GEMINI_TEXT_MODEL=gemini-2.5-pro
GEMINI_VISION_MODEL=gemini-2.5-pro

# Proxy Configuration (Optional)
HTTP_PROXY=http://your-proxy:port
HTTPS_PROXY=http://your-proxy:port
```

### 📊 Usage

#### Interactive Conversation

Have an interactive conversation with a specific API:

```bash
python main_new.py interactive --api monica
```

#### Multi-turn Conversation Testing

Test all APIs using predefined conversation flows:

```bash
python main_new.py multi-turn --file test_scenarios/comprehensive_test.json
```

#### Compare API Responses

Compare responses from different APIs to the same prompt:

```bash
python main_new.py compare --prompt "Explain the basic principles of quantum computing"
```

#### Batch Testing

Run a series of test cases:

```bash
python main_new.py batch --file test_scenarios/basic_test.json
```

### 📁 Project Structure

```
LLMBench/
├── aims/                  # Core code directory
│   ├── cli.py             # Command-line interface
│   ├── clients.py         # API client implementations
│   ├── evaluation.py      # Evaluation system
│   ├── models.py          # Data models
│   └── testing.py         # Testing tools
├── conversations/         # Conversation history storage
├── evaluations/           # Evaluation results storage
├── results/               # Test results storage
├── test_scenarios/        # Test scenario JSON files
└── main_new.py            # Main program entry
```

### 🔍 Evaluation Dimensions

AIBench evaluates AI response quality using the following dimensions:

| Dimension | Description | Weight |
|-----------|-------------|--------|
| Relevance | How relevant the answer is to the question | 25% |
| Accuracy | The accuracy and correctness of the answer | 25% |
| Completeness | The comprehensiveness and thoroughness of the answer | 20% |
| Coherence | The logic and fluency of the answer | 15% |
| Creativity | The innovation and uniqueness of the answer | 15% |

### 🧪 Test Scenarios

AIBench provides various preset test scenarios, including:

- **Basic Q&A**: Test basic knowledge and answering abilities
- **Context Memory**: Test the ability to remember context information
- **Chinese Language Understanding**: Test understanding of Chinese language and culture
- **Logical Reasoning**: Test logical reasoning and problem-solving abilities
- **Creative Generation**: Test creativity and imagination
- **Multi-turn Instructions**: Test the ability to execute complex instructions

### 📈 Custom Testing

Creating custom test scenarios is simple. Just create a JSON file in the following format:

```json
[
  {
    "name": "Test Name",
    "description": "Test Description",
    "turns": [
      {"prompt": "First round question"},
      {"prompt": "Second round question"}
    ]
  }
]
```

### 📝 Command Line Arguments

| Parameter | Short | Description |
|-----------|-------|-------------|
| `mode` | | Run mode: `interactive`, `compare`, `batch`, `multi-turn` |
| `--api` | `-a` | Specify API: `monica`, `openai`, `gemini`, `all` |
| `--prompt` | `-p` | Text prompt |
| `--image` | `-i` | Image URL |
| `--file` | `-f` | Test scenario JSON file |
| `--proxy` | | Set proxy |

### 📋 Evaluation Report Example

```
=== Overall API Scores ===
Monica API: 0.87 (Best)
OpenAI API: 0.85
Gemini API: 0.82

=== Dimension Breakdown ===
Relevance: Monica (0.92), OpenAI (0.89), Gemini (0.85)
Accuracy: OpenAI (0.90), Monica (0.88), Gemini (0.86)
Completeness: Monica (0.89), OpenAI (0.87), Gemini (0.82)
Coherence: Monica (0.85), OpenAI (0.84), Gemini (0.80)
Creativity: OpenAI (0.75), Monica (0.74), Gemini (0.70)
```

### 🤝 Contributing

Contributions of code, issue reports, or improvement suggestions are welcome! Please check the [contribution guidelines](CONTRIBUTING.md) for more information.

### 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### 📞 Contact

For any questions or suggestions, please contact us through:

- Email: your.email@example.com
- GitHub: [https://github.com/Gary-666/LLMBench](https://github.com/Gary-666/LLMBench)

---

<a id="chinese-version"></a>
## 中文版本

AIBench是一个强大的AI模型评估框架，专为比较和测试不同大语言模型API的对话能力而设计。通过标准化的测试场景和精确的评分系统，AIBench帮助您客观评估各种AI模型的性能表现。

### ✨ 主要特性

- **多API支持**: 同时测试和比较多个AI API（Monica、OpenAI、Gemini等）
- **多轮对话评估**: 测试AI在复杂对话流程中的表现
- **全面评分系统**: 基于相关性、准确性、完整性、连贯性和创新性进行评分
- **灵活模型配置**: 通过环境变量轻松配置每个API使用的模型
- **丰富测试场景**: 预设多种测试场景，覆盖基础问答、创意生成、逻辑推理等
- **详细评估报告**: 生成全面的评估报告，直观比较不同API的性能

### 🚀 快速开始

#### 安装

```bash
# 克隆仓库
git clone https://github.com/Gary-666/LLMBench.git
cd LLMBench

# 安装依赖
pip install -r requirements.txt
```

#### 配置

创建`.env`文件并添加您的API密钥和模型配置：

```
# API密钥
MONICA_KEY=your_monica_api_key
OPENAI_API_KEY=your_openai_api_key
GEMINI_KEY=your_gemini_api_key

# 模型配置
MONICA_MODEL=gpt-4o
OPENAI_TEXT_MODEL=gpt-4.1
OPENAI_VISION_MODEL=gpt-4.1
GEMINI_TEXT_MODEL=gemini-2.5-pro
GEMINI_VISION_MODEL=gemini-2.5-pro

# 代理配置（可选）
HTTP_PROXY=http://your-proxy:port
HTTPS_PROXY=http://your-proxy:port
```

### 📊 使用方法

#### 交互式对话

与特定API进行交互式对话：

```bash
python main_new.py interactive --api monica
```

#### 多轮对话测试

使用预定义的对话流程测试所有API：

```bash
python main_new.py multi-turn --file test_scenarios/comprehensive_test.json
```

#### 比较API响应

比较不同API对同一提示的响应：

```bash
python main_new.py compare --prompt "解释量子计算的基本原理"
```

#### 批量测试

运行一系列测试用例：

```bash
python main_new.py batch --file test_scenarios/basic_test.json
```

### 📁 项目结构

```
LLMBench/
├── aims/                  # 核心代码目录
│   ├── cli.py             # 命令行接口
│   ├── clients.py         # API客户端实现
│   ├── evaluation.py      # 评估系统
│   ├── models.py          # 数据模型
│   └── testing.py         # 测试工具
├── conversations/         # 对话历史存储
├── evaluations/           # 评估结果存储
├── results/               # 测试结果存储
├── test_scenarios/        # 测试场景JSON文件
└── main_new.py            # 主程序入口
```

### 🔍 评估维度

AIBench使用以下维度评估AI响应质量：

| 维度 | 描述 | 权重 |
|------|------|------|
| 相关性 | 回答与问题的相关程度 | 25% |
| 准确性 | 回答的准确性和正确性 | 25% |
| 完整性 | 回答的全面性和详尽程度 | 20% |
| 连贯性 | 回答的逻辑性和流畅度 | 15% |
| 创新性 | 回答的创新性和独特性 | 15% |

### 🧪 测试场景

AIBench提供多种预设测试场景，包括：

- **基础问答**: 测试基本知识和回答能力
- **上下文记忆**: 测试记住上下文信息的能力
- **中文理解**: 测试对中文语言和文化的理解
- **逻辑推理**: 测试逻辑推理和问题解决能力
- **创意生成**: 测试创造力和想象力
- **多轮指令**: 测试执行复杂指令的能力

### 📈 自定义测试

创建自定义测试场景很简单，只需按以下格式创建JSON文件：

```json
[
  {
    "name": "测试名称",
    "description": "测试描述",
    "turns": [
      {"prompt": "第一轮问题"},
      {"prompt": "第二轮问题"}
    ]
  }
]
```

### 📝 命令行参数

| 参数 | 简写 | 描述 |
|------|------|------|
| `mode` | | 运行模式: `interactive`, `compare`, `batch`, `multi-turn` |
| `--api` | `-a` | 指定API: `monica`, `openai`, `gemini`, `all` |
| `--prompt` | `-p` | 文本提示 |
| `--image` | `-i` | 图像URL |
| `--file` | `-f` | 测试场景JSON文件 |
| `--proxy` | | 设置代理 |

### 📋 评估报告示例

```
=== Overall API Scores ===
Monica API: 0.87 (最佳)
OpenAI API: 0.85
Gemini API: 0.82

=== Dimension Breakdown ===
相关性: Monica (0.92), OpenAI (0.89), Gemini (0.85)
准确性: OpenAI (0.90), Monica (0.88), Gemini (0.86)
完整性: Monica (0.89), OpenAI (0.87), Gemini (0.82)
连贯性: Monica (0.85), OpenAI (0.84), Gemini (0.80)
创新性: OpenAI (0.75), Monica (0.74), Gemini (0.70)
```

### 🤝 贡献

欢迎贡献代码、报告问题或提出改进建议！请查看[贡献指南](CONTRIBUTING.md)了解更多信息。

### 📄 许可证

本项目采用MIT许可证 - 详情请参阅[LICENSE](LICENSE)文件。

### 📞 联系方式

如有任何问题或建议，请通过以下方式联系我们：

- 邮箱: your.email@example.com
- GitHub: [https://github.com/Gary-666/LLMBench](https://github.com/Gary-666/LLMBench)

---

<p align="center">Made with ❤️ for the AI community</p>