import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../shared/theme.dart';
import '../../shared/widgets/app_ui.dart';
import 'compare_provider.dart';
import 'widgets/ai_analysis_card.dart';
import 'widgets/price_chart.dart';
import 'widgets/product_card.dart';
import 'widgets/same_list_item.dart';

class ComparePage extends ConsumerStatefulWidget {
  const ComparePage({super.key});

  @override
  ConsumerState<ComparePage> createState() => _ComparePageState();
}

class _ComparePageState extends ConsumerState<ComparePage> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final ctx = ref.read(pendingSearchProvider);
      if (ctx != null) {
        ref.read(compareProvider.notifier).loadFromContext(ctx);
        ref.read(pendingSearchProvider.notifier).state = null;
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final compareState = ref.watch(compareProvider);

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        leading: IconButton(
          tooltip: '返回首页',
          icon: const Icon(Icons.arrow_back),
          onPressed: _backToHome,
        ),
        title: const Text('比价结果'),
      ),
      body: _buildBody(compareState),
    );
  }

  Widget _buildBody(CompareState state) {
    switch (state.status) {
      case CompareStatus.loading:
        return Center(
          child: Padding(
            padding: const EdgeInsets.all(24),
            child: AppSurface(
              padding: const EdgeInsets.all(22),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const SizedBox(
                    width: 34,
                    height: 34,
                    child: CircularProgressIndicator(color: AppColors.primary),
                  ),
                  const SizedBox(height: 16),
                  const Text(
                    '正在识别同款与比价',
                    style: TextStyle(
                      fontSize: 17,
                      fontWeight: FontWeight.w800,
                      color: AppColors.textPrimary,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    state.lastSearch?.compareType == 1
                        ? '图片识别会先提取商品信息，再匹配相似商品。'
                        : '正在查询商品、价格趋势和可信店铺。',
                    textAlign: TextAlign.center,
                    style: const TextStyle(
                      fontSize: 13,
                      color: AppColors.textSecondary,
                    ),
                  ),
                ],
              ),
            ),
          ),
        );
      case CompareStatus.error:
        final isImage = state.lastSearch?.compareType == 1;
        return AppEmptyState(
          icon: isImage ? Icons.image_not_supported_outlined : Icons.cloud_off,
          title: isImage ? '图片比价失败' : '比价请求失败',
          message: isImage
              ? '没有识别出稳定的商品信息，可能是图片过暗、主体不清晰，或接口临时不可用。你可以换图，也可以改用关键词或链接继续比价。'
              : (state.errorMsg ?? '后端服务或网络请求异常，请稍后重试，或改用其他比价方式。'),
          primaryText: state.lastSearch == null ? '返回首页' : '重新尝试',
          onPrimary: state.lastSearch == null
              ? _backToHome
              : () => ref.read(compareProvider.notifier).retry(),
          actions: [
            OutlinedButton.icon(
              onPressed: () => _showManualKeywordDialog(context),
              icon: const Icon(Icons.manage_search),
              label: const Text('关键词比价'),
            ),
            const SizedBox(height: 8),
            OutlinedButton.icon(
              onPressed: () => _showManualUrlDialog(context),
              icon: const Icon(Icons.link),
              label: const Text('链接比价'),
            ),
          ],
        );
      case CompareStatus.done:
        final result = state.result!;
        if (result.compareList.isEmpty) {
          return _buildEmptyResult(result.goodsInfo);
        }
        final minPrice = result.compareList
            .where((g) => g.isOnSale)
            .map((g) => g.realPrice)
            .fold<double?>(null,
                (prev, price) => prev == null || price < prev ? price : prev);
        return SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              if (result.isMockData) _buildMockBanner(state.errorMsg),
              const SizedBox(height: 4),
              ProductCard(goodsInfo: result.goodsInfo),
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 16),
                child: Row(
                  children: [
                    Expanded(
                      child: _SummaryTile(
                        label: '最低价',
                        value: minPrice == null ? '-' : '¥${minPrice.toInt()}',
                        color: AppColors.priceRed,
                      ),
                    ),
                    const SizedBox(width: 10),
                    Expanded(
                      child: _SummaryTile(
                        label: '同款数',
                        value: '${result.compareList.length}',
                        color: AppColors.primary,
                      ),
                    ),
                    const SizedBox(width: 10),
                    Expanded(
                      child: _SummaryTile(
                        label: '建议',
                        value: result.aiAnalysis.priceLevel.isEmpty
                            ? '可参考'
                            : result.aiAnalysis.priceLevel,
                        color: AppColors.accent,
                      ),
                    ),
                  ],
                ),
              ),
              AiAnalysisCard(
                  analysis: result.aiAnalysis,
                  goodsInfo: result.goodsInfo,
                  compareList: result.compareList),
              PriceChart(priceHistory: result.priceHistory),
              const AppSectionTitle(
                title: '全网同款',
                subtitle: '默认按价格、同款可信度和店铺信息综合展示',
              ),
              ...result.compareList.asMap().entries.map((entry) {
                final goods = entry.value;
                return Column(
                  children: [
                    SameListItem(goods: goods),
                    if (entry.key < result.compareList.length - 1)
                      const Divider(height: 1, indent: 16, endIndent: 16),
                  ],
                );
              }),
              const SizedBox(height: 24),
            ],
          ),
        );
      case CompareStatus.idle:
        return _buildIdleState();
    }
  }

  Widget _buildIdleState() {
    return AppEmptyState(
      icon: Icons.manage_search,
      title: '还没有可显示的比价结果',
      message: '请返回首页重新发起图片、链接或关键词比价。',
      primaryText: '返回首页',
      onPrimary: _backToHome,
    );
  }

  Widget _buildEmptyResult(String goodsInfo) {
    return SingleChildScrollView(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const SizedBox(height: 4),
          ProductCard(goodsInfo: goodsInfo),
          const SizedBox(height: 48),
          Padding(
            padding: const EdgeInsets.all(24),
            child: AppSurface(
              padding: const EdgeInsets.all(20),
              child: Column(
                children: [
                  const AppIconBox(
                    icon: Icons.search_off,
                    color: AppColors.warning,
                    size: 56,
                  ),
                  const SizedBox(height: 14),
                  const Text(
                    '暂未找到同款商品',
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.w800,
                      color: AppColors.textPrimary,
                    ),
                  ),
                  const SizedBox(height: 8),
                  const Text(
                    '可以补充品牌、型号、容量等信息，或者换一张商品主体更清晰的图片。',
                    textAlign: TextAlign.center,
                    style: TextStyle(
                      fontSize: 13,
                      height: 1.55,
                      color: AppColors.textSecondary,
                    ),
                  ),
                  const SizedBox(height: 16),
                  ElevatedButton.icon(
                    onPressed: () => _showManualKeywordDialog(context),
                    icon: const Icon(Icons.manage_search),
                    label: const Text('补充关键词继续比价'),
                  ),
                  const SizedBox(height: 8),
                  OutlinedButton.icon(
                    onPressed: _backToHome,
                    icon: const Icon(Icons.home_outlined),
                    label: const Text('返回首页'),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  void _backToHome() {
    ref.read(compareProvider.notifier).reset();
    ref.read(pendingSearchProvider.notifier).state = null;
    context.go('/home');
  }

  void _showManualKeywordDialog(BuildContext context) {
    final controller = TextEditingController();
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('手动输入商品'),
        content: TextField(
          controller: controller,
          autofocus: true,
          textInputAction: TextInputAction.search,
          decoration: const InputDecoration(hintText: '例如：iPhone 16 Pro 256GB'),
          onSubmitted: (_) => _submitManualKeyword(ctx, controller),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('取消'),
          ),
          ElevatedButton(
            onPressed: () => _submitManualKeyword(ctx, controller),
            child: const Text('继续比价'),
          ),
        ],
      ),
    );
  }

  void _showManualUrlDialog(BuildContext context) {
    final controller = TextEditingController();
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('链接比价'),
        content: TextField(
          controller: controller,
          autofocus: true,
          decoration: const InputDecoration(hintText: '粘贴商品链接'),
          onSubmitted: (_) => _submitManualUrl(ctx, controller),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('取消'),
          ),
          ElevatedButton(
            onPressed: () => _submitManualUrl(ctx, controller),
            child: const Text('继续比价'),
          ),
        ],
      ),
    );
  }

  void _submitManualKeyword(
      BuildContext dialogContext, TextEditingController controller) {
    final keyword = controller.text.trim();
    if (keyword.isEmpty) return;
    Navigator.pop(dialogContext);
    ref.read(compareProvider.notifier).compareByKeyword(keyword);
  }

  void _submitManualUrl(
      BuildContext dialogContext, TextEditingController controller) {
    final url = controller.text.trim();
    if (url.isEmpty) return;
    Navigator.pop(dialogContext);
    ref.read(compareProvider.notifier).compareByUrl(url);
  }

  Widget _buildMockBanner(String? errorMsg) {
    return Container(
      margin: const EdgeInsets.fromLTRB(16, 4, 16, 0),
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
      decoration: BoxDecoration(
        color: const Color(0xFFFFF8E1),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: const Color(0xFFFFE082)),
      ),
      child: Row(
        children: [
          const Icon(Icons.info_outline, size: 18, color: Color(0xFFF57F17)),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              errorMsg == null || errorMsg.isEmpty
                  ? '当前显示为开发模拟数据。'
                  : '当前显示为开发模拟数据，原因：$errorMsg',
              style: const TextStyle(fontSize: 12, color: Color(0xFFBF360C)),
            ),
          ),
        ],
      ),
    );
  }
}

class _SummaryTile extends StatelessWidget {
  final String label;
  final String value;
  final Color color;

  const _SummaryTile({
    required this.label,
    required this.value,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return AppSurface(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 12),
      child: Column(
        children: [
          Text(label,
              style: const TextStyle(
                  fontSize: 11, color: AppColors.textSecondary)),
          const SizedBox(height: 4),
          Text(
            value,
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
            style: TextStyle(
              fontSize: 17,
              fontWeight: FontWeight.w900,
              color: color,
            ),
          ),
        ],
      ),
    );
  }
}
