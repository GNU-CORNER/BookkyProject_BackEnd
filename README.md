# BookkyProject_BackEnd
BackEnd for BookkyProject

### :)

#API Schma
# BASE URL = “http://203.255.3.144:8002/v1”

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

# USER-API

### 회원가입 [’POST’]

- URL = “http://203.255.3.144:8002/v1/user/signup

```json
{//body
	"email" : String,  //사용자 이메일
	"nickname" : String, //사용자 닉네임
	"pwToken" : String	//사용자 비밀번호 (서버에서 알아서 인코딩 되니깐 RAW데이터로 보내도 됨)
}
```

```json
{
		"success": Boolean,
		"result" : {
		    "email" : String,
				"nickname" : String,
				"pushToken" : String,
				"pushNoti" : Boolean,
				"thumbnail" : String
		},
		"errorMessage": String,
		"access_token" : String,
		"refresh_token" : String
}
```

### 로그인 [’POST’]

- URL = “http://203.255.3.144:8002/v1/user/signin

```json
{//body
			"email" : String,  //사용자 이메일
			"pwToken" : String	//사용자 비밀번호 (서버에서 알아서 인코딩 되니깐 RAW데이터로 보내도 됨)
}
```

```json
{
  	"success": Boolean,
		"result" : {
				"email" : String,
				"nickname" : String,
				"pushToken" : String,
				"pushNoti" : Boolean,
        "thumbnail" : String
		},
		"errorMessage": String,
		"access_token" : String,
		"refresh_token" : String
}
```

### 로그아웃[’POST’]

- URL =  “http://203.255.3.144:8002/v1/user/signout

```json
{//headers
			"access-token" : String,  //접근 토큰
			"refresh-token" : String	//갱신 토큰
}
```

```json
{
    "success": Boolean,
    "result": {},
    "errorMessage": String
}
```

### 회원정보 수정[’PUT’]

- URL = “http://203.255.3.144:8002/v1/user

```json
{//headers
			"access-token" : String
}
{//body "원하는 값만 넣어서 업데이트 가능"
			//Optional
	  "nickname": String, 
			//Optional
	  "thumbnail": String, 
			//Optional
	  "pushNoti": Boolean,
			//Optional
	  "pushToken": String
}
```

```json
{
    "success": Boolean,
    "result": {
        "email": String,
        "nickname": String,
        "pushToken": String,
        "pushNoti": Boolean,
        "thumbnail": String
    },
    "errorMessage": String
}
```

### 회원탈퇴[’DELETE’]

- URL = “http://203.255.3.144:8002/v1/user

```json
{//headers 
			"access-token" : String
}
```

```json
{
    "success": Boolean,
    "result": {},
    "errorMessage": String
}
```

### 이메일 인증 코드 전송[’POST’]

- URL = “http://203.255.3.144:8002/v1/user/email”
- 인증코드 만료시간 3분임

```json
{
    "email": String //중복처리까지 같이 함
}
```

```json
{
    "success": Boolean, //False 이면 중복
    "result": {
        "email": String
    },
    "errorMessage": String
}
```

### 이메일 인증 코드 확인 [’POST’]

- URL = “http://203.255.3.144:8002/v1/user/check”

```json
{
    "email": String,
    "code": Integer
}
```

```json
{
    "success": Boolean,
    "result": {},
    "errorMessage": String
}
```

# Authorization-API

### Access-Token 갱신[’POST’]

- URL = “[http://203.255.3.144:8002/v1/auth/refresh](http://203.255.3.144:8002/v1/auth/refresh)”

```json
{//header
	"access-token" : String,
	"refresh-token" : String
}
```

```json
{
    "success": Boolean,
    "result": {},
    "errorMessage": String,
    "access_token": String
}
```
