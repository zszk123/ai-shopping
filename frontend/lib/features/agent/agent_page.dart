import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../shared/models/agent_chat.dart';
import '../../shared/theme.dart';
import '../../shared/widgets/app_ui.dart';
import 'agent_provider.dart';

class AgentPage extends ConsumerStatefulWidget {
  const AgentPage({super.key});

  @override
  ConsumerState<AgentPage> createState() => _AgentPageState();
}

class _AgentPageState extends ConsumerState<AgentPage> {
  final _controller = TextEditingController();
  final _scrollController = ScrollController();

  @override
  void dispose() {
    _controller.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(agentProvider);

    ref.listen(agentProvider, (_, __) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        if (!_scrollController.hasClients) return;
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 220),
          curve: Curves.easeOut,
        );
      });
    });

    return Scaffold(
      appBar: AppBar(
        title: const Text('AI 客服'),
        automaticallyImplyLeading: false,
        actions: [
          IconButton(
            tooltip: '清空会话',
            onPressed: () => ref.read(agentProvider.notifier).clear(),
            icon: const Icon(Icons.delete_sweep_outlined),
          ),
        ],
      ),
      body: Column(
        children: [
          const _AgentIntro(),
          Expanded(
            child: ListView.builder(
              controller: _scrollController,
              padding: const EdgeInsets.fromLTRB(12, 10, 12, 8),
              itemCount: state.messages.length + (state.isLoading ? 1 : 0),
              itemBuilder: (context, index) {
                if (index >= state.messages.length) {
                  return const _TypingBubble();
                }
                return _MessageBubble(message: state.messages[index]);
              },
            ),
          ),
          _QuickPrompts(onTap: _sendText),
          _InputBar(
            controller: _controller,
            enabled: !state.isLoading,
            onSend: () {
              final text = _controller.text;
              _controller.clear();
              _sendText(text);
            },
          ),
        ],
      ),
    );
  }

  void _sendText(String text) {
    ref.read(agentProvider.notifier).send(text);
  }
}

class _AgentIntro extends StatelessWidget {
  const _AgentIntro();

  @override
  Widget build(BuildContext context) {
    return const Padding(
      padding: EdgeInsets.fromLTRB(16, 4, 16, 0),
      child: AppSurface(
        padding: EdgeInsets.all(14),
        child: Row(
          children: [
            AppIconBox(icon: Icons.support_agent, color: AppColors.accent),
            SizedBox(width: 12),
            Expanded(
              child: Text(
                '可以问商品推荐、价格判断、失败原因和项目运行问题。客服仅支持文字输入。',
                style: TextStyle(
                  fontSize: 13,
                  height: 1.45,
                  color: AppColors.textSecondary,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _MessageBubble extends StatelessWidget {
  final ChatMessage message;

  const _MessageBubble({required this.message});

  @override
  Widget build(BuildContext context) {
    final isUser = message.isUser;
    return Align(
      alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
      child: ConstrainedBox(
        constraints:
            BoxConstraints(maxWidth: MediaQuery.sizeOf(context).width * 0.78),
        child: Container(
          margin: const EdgeInsets.symmetric(vertical: 5),
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
          decoration: BoxDecoration(
            color: isUser ? AppColors.primary : Colors.white,
            borderRadius: BorderRadius.circular(12),
            border: isUser ? null : Border.all(color: AppColors.divider),
          ),
          child: Text(
            message.content,
            style: TextStyle(
              fontSize: 14,
              height: 1.45,
              color: isUser ? Colors.white : AppColors.textPrimary,
            ),
          ),
        ),
      ),
    );
  }
}

class _TypingBubble extends StatelessWidget {
  const _TypingBubble();

  @override
  Widget build(BuildContext context) {
    return const Align(
      alignment: Alignment.centerLeft,
      child: Padding(
        padding: EdgeInsets.symmetric(horizontal: 4, vertical: 8),
        child: AppSurface(
          padding: EdgeInsets.all(10),
          child: SizedBox(
            width: 22,
            height: 22,
            child: CircularProgressIndicator(strokeWidth: 2),
          ),
        ),
      ),
    );
  }
}

class _QuickPrompts extends StatelessWidget {
  final ValueChanged<String> onTap;

  const _QuickPrompts({required this.onTap});

  @override
  Widget build(BuildContext context) {
    const prompts = ['帮我比价 iPhone 16 256G', '查看我的历史记录', '图片比价为什么失败'];
    return SizedBox(
      height: 46,
      child: ListView.separated(
        scrollDirection: Axis.horizontal,
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 5),
        itemBuilder: (context, index) {
          final text = prompts[index];
          return ActionChip(
            label: Text(text),
            onPressed: () => onTap(text),
            labelStyle: const TextStyle(fontSize: 12),
            side: const BorderSide(color: AppColors.divider),
            backgroundColor: Colors.white,
          );
        },
        separatorBuilder: (_, __) => const SizedBox(width: 8),
        itemCount: prompts.length,
      ),
    );
  }
}

class _InputBar extends StatelessWidget {
  final TextEditingController controller;
  final bool enabled;
  final VoidCallback onSend;

  const _InputBar({
    required this.controller,
    required this.enabled,
    required this.onSend,
  });

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      top: false,
      child: Container(
        padding: const EdgeInsets.fromLTRB(12, 8, 12, 10),
        decoration: const BoxDecoration(
          color: Colors.white,
          border: Border(top: BorderSide(color: AppColors.divider)),
        ),
        child: Row(
          children: [
            Expanded(
              child: TextField(
                controller: controller,
                enabled: enabled,
                minLines: 1,
                maxLines: 4,
                textInputAction: TextInputAction.send,
                decoration: const InputDecoration(hintText: '问商品、价格、历史或运行问题'),
                onSubmitted: (_) => enabled ? onSend() : null,
              ),
            ),
            const SizedBox(width: 8),
            SizedBox(
              width: 46,
              height: 46,
              child: IconButton.filled(
                tooltip: '发送',
                onPressed: enabled ? onSend : null,
                icon: const Icon(Icons.send),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
