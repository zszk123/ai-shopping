class AgentToolResult {
  final String tool;
  final String summary;
  final dynamic data;

  const AgentToolResult({
    required this.tool,
    required this.summary,
    this.data,
  });

  factory AgentToolResult.fromJson(Map<String, dynamic> json) {
    return AgentToolResult(
      tool: json['tool'] as String? ?? '',
      summary: json['summary'] as String? ?? '',
      data: json['data'],
    );
  }
}

class AgentReply {
  final String reply;
  final String intent;
  final List<AgentToolResult> toolResults;
  final bool needLogin;

  const AgentReply({
    required this.reply,
    required this.intent,
    this.toolResults = const [],
    this.needLogin = false,
  });

  factory AgentReply.fromJson(Map<String, dynamic> json) {
    return AgentReply(
      reply: json['reply'] as String? ?? '',
      intent: json['intent'] as String? ?? '',
      toolResults: (json['tool_results'] as List<dynamic>?)
              ?.map((item) =>
                  AgentToolResult.fromJson(item as Map<String, dynamic>))
              .toList() ??
          [],
      needLogin: json['need_login'] as bool? ?? false,
    );
  }
}

class ChatMessage {
  final String role;
  final String content;
  final DateTime createTime;
  final bool isImage;

  const ChatMessage({
    required this.role,
    required this.content,
    required this.createTime,
    this.isImage = false,
  });

  bool get isUser => role == 'user';

  Map<String, String> toHistoryJson() {
    return {'role': role, 'content': content};
  }
}
