class User {
  final int id;
  final String username;
  final String phone;
  final String avatar;

  const User({
    required this.id,
    required this.username,
    required this.phone,
    this.avatar = '',
  });

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'] as int,
      username: json['username'] as String,
      phone: json['phone'] as String? ?? '',
      avatar: json['avatar'] as String? ?? '',
    );
  }

  String get maskedPhone {
    if (phone.length != 11) return phone;
    return '${phone.substring(0, 3)}****${phone.substring(7)}';
  }
}
