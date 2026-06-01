import 'dart:typed_data';

import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../shared/models/agent_chat.dart';
import '../../shared/services/api_client.dart';

class AgentState {
  final List<ChatMessage> messages;
  final bool isLoading;
  final String? errorMsg;

  const AgentState({
    this.messages = const [],
    this.isLoading = false,
    this.errorMsg,
  });

  AgentState copyWith({
    List<ChatMessage>? messages,
    bool? isLoading,
    String? errorMsg,
  }) {
    return AgentState(
      messages: messages ?? this.messages,
      isLoading: isLoading ?? this.isLoading,
      errorMsg: errorMsg,
    );
  }
}

class AgentNotifier extends StateNotifier<AgentState> {
  final ApiClient _api;

  AgentNotifier(this._api)
      : super(AgentState(messages: [
          ChatMessage(
            role: 'assistant',
            content: '你好，我是 AI 客服。可以帮你比价、解释购买建议、查看历史记录，也能协助排查运行问题。',
            createTime: DateTime.now(),
          ),
        ]));

  Future<void> send(String text) async {
    final message = text.trim();
    if (message.isEmpty || state.isLoading) return;

    final userMessage = ChatMessage(
      role: 'user',
      content: message,
      createTime: DateTime.now(),
    );
    final updatedMessages = [...state.messages, userMessage];
    state = state.copyWith(
      messages: updatedMessages,
      isLoading: true,
      errorMsg: null,
    );

    try {
      final history = updatedMessages
          .where((item) => item.content.isNotEmpty)
          .take(10)
          .map((item) => item.toHistoryJson())
          .toList();
      final data = await _api.agentChat(message: message, history: history);
      final reply = AgentReply.fromJson(data);
      state = state.copyWith(
        messages: [
          ...updatedMessages,
          ChatMessage(
            role: 'assistant',
            content: reply.reply,
            createTime: DateTime.now(),
          ),
        ],
        isLoading: false,
      );
    } on ApiException catch (e) {
      _appendError(updatedMessages, e.message);
    } catch (_) {
      _appendError(updatedMessages, 'AI 客服暂时不可用，请稍后重试');
    }
  }

  Future<void> sendImage(Uint8List imageBytes, {String message = ''}) async {
    if (state.isLoading) return;

    final displayText = message.trim().isEmpty ? '发送了一张商品图片' : message.trim();
    final userMessage = ChatMessage(
      role: 'user',
      content: displayText,
      createTime: DateTime.now(),
      isImage: true,
    );
    final updatedMessages = [...state.messages, userMessage];
    state = state.copyWith(
      messages: updatedMessages,
      isLoading: true,
      errorMsg: null,
    );

    try {
      final data = await _api.agentChatImage(
        imageBytes: imageBytes,
        message: message,
      );
      final reply = AgentReply.fromJson(data);
      state = state.copyWith(
        messages: [
          ...updatedMessages,
          ChatMessage(
            role: 'assistant',
            content: reply.reply,
            createTime: DateTime.now(),
          ),
        ],
        isLoading: false,
      );
    } on ApiException catch (e) {
      _appendError(updatedMessages, e.message);
    } catch (_) {
      _appendError(updatedMessages, '图片客服暂时不可用，请稍后重试');
    }
  }

  void clear() {
    state = AgentState(messages: [
      ChatMessage(
        role: 'assistant',
        content: '会话已清空。你可以继续问我商品比价、购买建议或运行排查问题。',
        createTime: DateTime.now(),
      ),
    ]);
  }

  void _appendError(List<ChatMessage> messages, String error) {
    state = state.copyWith(
      messages: [
        ...messages,
        ChatMessage(
          role: 'assistant',
          content: error,
          createTime: DateTime.now(),
        ),
      ],
      isLoading: false,
      errorMsg: error,
    );
  }
}

final agentProvider = StateNotifierProvider<AgentNotifier, AgentState>((ref) {
  final api = ref.watch(apiClientProvider);
  return AgentNotifier(api);
});
