# BookkyProject_BackEnd
BackEnd for BookkyProject

### :)

#API Schma

# BASE Response

```json
{
	"success" : Boolean,
	"result" : {},
	"errorMessage" : String
}
```

# BASE Header

```json
{
	"access-token" : String,
	"refresh-token" : String
}
```

### 토큰 갱신 (POST)
- URL = /auth/refresh
- Require = HEADER(access-token, refresh-token)

- RESPONSE
```json
{
  "success": BOOLEAN,
  "result": {
    "access_token": STRING
  },
  "errorMessage": STRING
}
```

### 책 디테일 (GET)
- URL = /books/{slug}
- Require = QUERY(SLUG)
- Description = slug = 0은 TAG구분없이 보냄, slug != 0은 해당 slug의 BID값에 맞는 책을 넘겨줌

- RESPONSE
```json
{
  "success": BOOLEAN,
  "result": {
    "bookList": [
      {
        "TITLE": STRING,
        "SUBTITLE": STRING,
        "AUTHOR": STRING,
        "ISBN": STRING,
        "PUBLISHER": STRING,
        "PRICE": STRING,
        "PAGE": STRING,
        "BOOK_INDEX": STRING,
        "BOOK_INTRODUCTION": STRING,
        "Allah_BID": STRING,
        "PUBLISH_DATE": STRING,
        "thumbnail": STRING,
        "thumbnailImage": STRING
      }
    ],
    "isFavorite": BOOLEAN
  },
  "errorMessage": STRING
}
```

### 홈 데이터 (GET)
- URL = /home
- Optional = HEADER(access-token)
- 회원일때 access-token 포함

- RESPONSE
```json
{
  "success": BOOLEAN,
  "result": {
    "bookList": [
      {
        "tag": STRING,
        "data": [
          {
            "BID": INTEGER,
            "TITLE": STRING,
            "AUTHOR": STRING,
            "thumbnailImage": STRING
          }
        ]
      }
    ],
    "communityList": [
      {}
    ],
    "userData": {
      "UID": INTEGER,
      "tag_array": [
        STRING
      ],
      "nickname": STRING,
      "thumbnail": STRING
    }
  },
  "errorMessage": STRING
}
```

### 태그 데이터 (GET)
- URL = /tags
```json

- RESPONSE
{
  "success": BOOLEAN,
  "result": {
    "tag": [
      {
        "TID": INTEGER,
        "nameTag": STRING
      }
    ]
  },
  "errorMessage": STRING
}
```

### 유저 수정 (PUT)
- URL = /user
- Require = HEADER(access-token)

- BODY
```json
{
  "email": STRING
}
```

- RESPONSE
```json
{
  "success": BOOLEAN,
  "result": {
    "userData": {
      "email": STRING
    }
  },
  "errorMessage": STRING
}
```

### 유저 탈퇴 (DELETE)
- URL = /user
- Require = HEADER(access-token)

- RESPONSE
```json
{
  "success": BOOLEAN,
  "result": {},
  "errorMessage": STRING
}
```

### 인증코드 확인 (POST)
- URL = /user/check
- BODY
```json
{
  "email": STRING,
  "code": INTEGER
}
```

- RESPONSE
```json
{
  "success": BOOLEAN,
  "result": {},
  "errorMessage": STRING
}
```

### 인증코드 발송 (GET)
- URL = /user/email
- 보내고 나서 3분 유효기간 시작, 호출 즉시 시작됨
- Require = QUERY(email)


- RESPONSE
```json
{
  "success": BOOLEAN,
  "result": {
    "email": STRING
  },
  "errorMessage": STRING
}
```

### 관심도서 등록 (POST)
- URL = /user/favoritebook
- Require = Header(access-token)

- BODY
```json
{
  "BID": INTEGER
}
```

- Response
```json
{
  "success": BOOLEAN,
  "result": {
    "favoriteItem": {
      "BID": INTEGER,
      "UID": INTEGER
    }
  },
  "errorMessage": STRING
}
```

### 관심도서 삭제 (DELETE)
- URL = /user/favoritebook
- Require = Header(access-token)

- BODY
```json
{
  "BID": INTEGER
}
```

- Response
```json
{
  "success": BOOLEAN,
  "result": {},
  "errorMessage": STRING
}
```

### 닉네임 중복 확인 (GET)
- URL = /user/nickname
- Require = QUERY(nickname)

- Response
```json
{
  "success": BOOLEAN,
  "result": {
    "nickname": STRING
  },
  "errorMessage": STRING
}
```

### 로그인 (POST)
- URL = /user/signin

- BODY
```json
{
  "email": STRING,
  "pwToken": STRING,
  "loginMethod": INTEGER
}
```

- RESPONSE
```json
{
  "success": BOOLEAN,
  "result": {
    "userData": {
      "email": STRING,
      "nickname": STRING,
      "pushToken": STRING,
      "pushNoti": BOOLEAN,
      "thumbnail": STRING,
      "loginMethod": INTEGER
    },
    "access_token": STRING,
    "refresh_token": STRING
  },
  "errorMessage": STRING
}
```

### 회원가입 (POST)
- URL = /user/signup

- BODY
```json
{
  "email": STRING,
  "nickname": STRING,
  "pwToken": STRING,
  "loginMethod": INTEGER
}
```

- RESPONSE
```json
{
  "success": BOOLEAN,
  "result": {
    "userData": {
      "email": STRING,
      "nickname": STRING,
      "pushToken": STRING,
      "pushNoti": BOOLEAN,
      "thumbnail": STRING,
      "loginMethod": INTEGER
    },
    "access_token": STRING,
    "refresh_token": STRING
  },
  "errorMessage": STRING
}
```

### 로그아웃(POST)
- URL = /user/signout
- Require = HEADER(access-token, refresh-token)

- RESPONSE
```json
{
  "success": BOOLEAN,
  "result": {},
  "errorMessage": STRING
}
```

### 사용자 관심분야 (PUT)
- URL = /user/tag
- Require = Header(access-token)

- BODY
```json
{
  "tag": [
    INTEGER
  ]
}
```

- RESPONSE
```json
{
  "success": BOOLEAN,
  "result": {
    "tag": [
      STRING
    ]
  },
  "errorMessage": STRING
}
```
