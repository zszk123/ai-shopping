import '../models/user.dart';

const mockUsers = [
  User(id: 1, username: '小明', phone: '13812345678'),
  User(id: 2, username: '购物达人', phone: '13987654321'),
];

const mockToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.mock_token';

Map<String, dynamic> mockLoginResponse(User user) {
  return {
    'code': 200,
    'msg': '登录成功',
    'data': {
      'token': mockToken,
      'user_id': user.id,
      'username': user.username,
      'phone': user.phone,
    },
  };
}
