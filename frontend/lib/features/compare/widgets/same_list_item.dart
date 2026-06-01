import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
import '../../../shared/models/goods.dart';
import '../../../shared/theme.dart';
import '../../../shared/widgets/app_ui.dart';

class SameListItem extends StatelessWidget {
  final Goods goods;

  const SameListItem({super.key, required this.goods});

  @override
  Widget build(BuildContext context) {
    final isOff = goods.isOffShelf;

    return Opacity(
      opacity: isOff ? 0.45 : 1.0,
      child: Padding(
        padding: const EdgeInsets.fromLTRB(16, 0, 16, 10),
        child: AppSurface(
          padding: const EdgeInsets.all(12),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              _PlatformBadge(
                  label: goods.platformLabel, color: _platformColor()),
              const SizedBox(width: 10),
              _ProductImage(goods: goods, isOff: isOff),
              const SizedBox(width: 10),
              Expanded(child: _ProductInfo(goods: goods, isOff: isOff)),
              const SizedBox(width: 8),
              _PriceAction(goods: goods, isOff: isOff),
            ],
          ),
        ),
      ),
    );
  }

  Color _platformColor() {
    switch (goods.platform) {
      case 'jingdong':
      case '京东':
        return const Color(0xFFE4393C);
      case 'taobao':
      case '淘宝':
        return const Color(0xFFFF5000);
      case 'pdd':
      case '拼多多':
        return const Color(0xFFE02E24);
      case 'douyin':
      case '抖音':
        return const Color(0xFF010101);
      default:
        return AppColors.primary;
    }
  }
}

class _PlatformBadge extends StatelessWidget {
  final String label;
  final Color color;

  const _PlatformBadge({required this.label, required this.color});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 40,
      height: 36,
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Center(
        child: Text(
          label,
          style: TextStyle(
              fontSize: 10, fontWeight: FontWeight.w600, color: color),
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
        ),
      ),
    );
  }
}

class _ProductImage extends StatelessWidget {
  final Goods goods;
  final bool isOff;

  const _ProductImage({required this.goods, required this.isOff});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 60,
      height: 60,
      decoration: BoxDecoration(
        color: AppColors.background,
        borderRadius: BorderRadius.circular(8),
      ),
      child: goods.goodsImg.isNotEmpty
          ? ClipRRect(
              borderRadius: BorderRadius.circular(8),
              child: Image.network(goods.goodsImg,
                  width: 60,
                  height: 60,
                  fit: BoxFit.cover,
                  errorBuilder: (_, __, ___) => Icon(
                        Icons.shopping_bag,
                        color: isOff
                            ? AppColors.disabled
                            : AppColors.textSecondary,
                        size: 24,
                      )),
            )
          : Icon(Icons.shopping_bag,
              color: isOff ? AppColors.disabled : AppColors.textSecondary,
              size: 24),
    );
  }
}

class _ProductInfo extends StatelessWidget {
  final Goods goods;
  final bool isOff;

  const _ProductInfo({required this.goods, required this.isOff});

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          '${goods.goodsName} ${goods.specParam}',
          style: TextStyle(
            fontSize: 13,
            fontWeight: FontWeight.w500,
            color: isOff ? AppColors.disabled : AppColors.textPrimary,
            decoration: isOff ? TextDecoration.lineThrough : null,
          ),
          maxLines: 2,
          overflow: TextOverflow.ellipsis,
        ),
        const SizedBox(height: 4),
        Wrap(
          spacing: 6,
          runSpacing: 4,
          children: [
            if (goods.shopName.isNotEmpty)
              _MetaText(goods.shopName, isOff: isOff),
            if (goods.couponDesc.isNotEmpty)
              _MetaText(goods.couponDesc, color: AppColors.priceRed),
            _MetaText('销量 ${goods.salesText}', isOff: isOff),
          ],
        ),
        const SizedBox(height: 6),
        Wrap(
          spacing: 6,
          runSpacing: 4,
          children: [
            if (goods.matchScore > 0)
              _ScoreChip('同款 ${goods.matchScore.toStringAsFixed(0)}'),
            if (goods.trustScore > 0)
              _ScoreChip(
                  '${goods.trustLabel} ${goods.trustScore.toStringAsFixed(0)}'),
          ],
        ),
      ],
    );
  }
}

class _MetaText extends StatelessWidget {
  final String text;
  final bool isOff;
  final Color? color;

  const _MetaText(this.text, {this.isOff = false, this.color});

  @override
  Widget build(BuildContext context) {
    return Text(
      text,
      style: TextStyle(
          fontSize: 11,
          color:
              color ?? (isOff ? AppColors.disabled : AppColors.textSecondary)),
    );
  }
}

class _ScoreChip extends StatelessWidget {
  final String text;

  const _ScoreChip(this.text);

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
      decoration: BoxDecoration(
        color: AppColors.primary.withValues(alpha: 0.08),
        borderRadius: BorderRadius.circular(4),
      ),
      child: Text(text,
          style: const TextStyle(fontSize: 10, color: AppColors.primary)),
    );
  }
}

class _PriceAction extends StatelessWidget {
  final Goods goods;
  final bool isOff;

  const _PriceAction({required this.goods, required this.isOff});

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.end,
      children: [
        Text(
          '¥${goods.realPrice.toStringAsFixed(0)}',
          style: TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.bold,
            color: isOff ? AppColors.disabled : AppColors.priceRed,
            decoration: isOff ? TextDecoration.lineThrough : null,
          ),
        ),
        if (goods.originalPrice > goods.realPrice)
          Text(
            '¥${goods.originalPrice.toStringAsFixed(0)}',
            style: const TextStyle(
              fontSize: 11,
              color: AppColors.textSecondary,
              decoration: TextDecoration.lineThrough,
            ),
          ),
        const SizedBox(height: 4),
        if (!isOff)
          SizedBox(
            height: 28,
            child: ElevatedButton(
              onPressed: () {
                if (goods.goodsUrl.isNotEmpty) {
                  final uri = Uri.tryParse(goods.goodsUrl);
                  if (uri != null) {
                    launchUrl(uri, mode: LaunchMode.externalApplication);
                  }
                }
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: AppColors.primary,
                minimumSize: const Size(64, 28),
                padding: const EdgeInsets.symmetric(horizontal: 10),
                shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(14)),
                textStyle: const TextStyle(fontSize: 11),
              ),
              child: const Text('购买'),
            ),
          ),
        if (isOff)
          const Text('已下架',
              style: TextStyle(fontSize: 11, color: AppColors.disabled)),
      ],
    );
  }
}
