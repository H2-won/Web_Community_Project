import os
from api import api
from flask import request, redirect
from flask import jsonify,current_app
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from models import User, db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from werkzeug.utils import secure_filename

# 임시
from flask import g
# 이미지 기본 설정
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
UPLOAD_FOLDER = 'static/img/profile_img'
def allowed_file(file):
   check = 1
   if file.filename.rsplit('.', 1)[1].lower() not in ALLOWED_EXTENSIONS or '.' not in file.filename:
      check = 0
         
   return check

# 프로필 사진 업로드
@api.route('/profile_img_upload/<id>', methods=['POST']) 
@jwt_required
def projile_img_upload(id):
	profile_img = request.files['profile_img']		# 프로필 사진 받아도 되고 안받아도 됨
	# POST request에 파일 정보가 있는지 확인
	print(request.files)

	if 'profile_img' not in request.files:
		print('No file part')
		return redirect('api/progile_img_upload/<id>')

	# 만약 유저가 파일을 고르지 않았을 경우
	if profile_img.filename == '':
		print('No selected file')
		return redirect('api/progile_img_upload/<id>')
	
	# 프로필 사진 이름 유저 테이블에 삽입 및 저장
	if profile_img and allowed_file(profile_img):		# 프로필 이미지 확장자 확인
		suffix = datetime.now().strftime("%y%m%d_%H%M%S")				
		filename = "_".join([profile_img.filename.rsplit('.', 1)[0], suffix])			# 중복된 이름의 사진을 받기위해서 파일명에 시간을 붙임
		extension = profile_img.filename.rsplit('.', 1)[1]
		filename = secure_filename(f"{filename}.{extension}")

		user = User.query.filter(User.id == id).first()
		user.profile_img = filename
		db.session.add(user)
		db.session.commit()

		profile_img.save(os.path.join(UPLOAD_FOLDER, filename))
		return {"msg": "프로필 사진 등록 완료"}, 201
	return	{"msg": "프로필 사진 등록이 안댓다"}, 404

# request.form.get()
@api.route('/sign_up', methods=['POST'])# 회원 가입 api 및 임시로 데이터 확인api
def sign_up():
	
	# 6개 데이터 받기(실명, 생년월일, 아이디, 비번, 이메일, 닉네임)
	userid = request.form.get('userid')
	username = request.form.get('username')
	nickname = request.form.get('nickname')
	birth = request.form.get('birth')		# 생년월일를 보낼 때는 YYYY-MM-XX형식으로
	email = request.form.get('email')
	password = request.form.get('password')
	repassword = request.form.get('repassword')
	
	try:		# 프로필 사진 받아도 되고 안받아도 됨
		profile_img = request.files['profile_img']
	except:
		profile_img = None
	
	dt = datetime.strptime(birth, "%Y-%m-%d")# json형식으로 받은 data를 날짜 형식으로 변환

	if User.query.filter(User.userid == userid).first():# id중복 검사
		return jsonify({'error':'already exist'}), 400
	
	if not (userid and username and password and repassword and birth):# email를 제외한 5가지중 하나라도 입력받지 못한 경우 오류 코드
		return jsonify({'error': 'No arguments'}), 400
	if password != repassword:# 비밀번호 재확인과 비밀번호 일치 확인 코드
		return jsonify({'error':'Wrong password'}), 400
	
	# db 6개 회원정보 저장
	user = User()
	user.userid = userid
	user.username = username
	user.birth = dt
	user.nickname = nickname
	user.email = email
	user.password = generate_password_hash(password)# 비밀번호 해시
	
	
	# 프로필 사진 이름 유저 테이블에 삽입 및 저장
	if profile_img and allowed_file(profile_img):		# 프로필 이미지 확장자 확인
		suffix = datetime.now().strftime("%y%m%d_%H%M%S")				
		filename = "_".join([profile_img.filename.rsplit('.', 1)[0], suffix])			# 중복된 이름의 사진을 받기위해서 파일명에 시간을 붙임
		extension = profile_img.filename.rsplit('.', 1)[1]
		filename = secure_filename(f"{filename}.{extension}")
		profile_img.save(os.path.join(UPLOAD_FOLDER, filename))
		user.profile_img = filename


	db.session.add(user)
	db.session.commit()
	response_object = {
		'status': '성공'
	}
	return jsonify(response_object), 201
	
	# users = User.query.all()
	# return jsonify([user.serialize for user in users])# 모든 사용자정보 반환
	# res_users = {}
	# for user in users:# 반복문을 돌면서 직렬화된 변수를 넣어서 새로운 리스트를 만든다.
	#     res_users.append(user.serialize)
	# return jsonify(res_users)


# 로그인 api 
@api.route('/login', methods=['POST'])
def login():
	# id와 패스워드 받기
	data = request.get_json()
	userid = data.get('userid')
	password = data.get('password')

	user = User.query.filter(User.userid == userid).first()
	
	if user is None and userid != current_app.config['ADMIN_ID']:
		return jsonify(
			result = "not found"
		)
	if userid == current_app.config['ADMIN_ID']:		# 관리자 아이디 권한 부여
		if password == current_app.config['ADMIN_PW']:
			return jsonify(
				result = "success",
				access_token = create_access_token(
					identity = userid,
					expires_delta = False
				)
			)
	if check_password_hash(user.password, password):		# 해시화한 비밀번호 비교하기
		return jsonify(
			result = "success",
			access_token = create_access_token(
				identity = userid,
				expires_delta = False
			)
		)
	else:
		return jsonify(result = "incorrect Password")


# 유저정보 반환
@api.route('/user_info', methods=['GET'])
@jwt_required		# 데코레이터로 로그인 사용자만 화면에 접근할 수 있게 하는 구문,이 구문이 있는 페이지에 들어가려면  Authorization에 토큰을 보내주어야한다.
def user_info():
	check_user = get_jwt_identity()		# 토큰에서 identity꺼내서 userid를 넣는다.
	access_user = User.query.filter(User.userid == check_user).first()# 꺼낸 토큰이 유효한 토큰인지 확인
	if access_user is None:		# 제대로 된 토큰인지 확인
		return "user only"
	else:
		return jsonify(access_user.serialize)# 모든 사용자정보 반환

	# ------------------------------신경 안써도댐------------------------------
	#  res_users = {}
	#  for user in users:# 반복문을 돌면서 직렬화된 변수를 넣어서 새로운 리스트를 만든다.
	#      res_users.append(user.serialize)
	#  return jsonify(res_users)
	# ------------------------------------------------------------------------

# 해당 유저 정보 전부 반환
@api.route('/users_all_info')
def users_all_info():
	users = User.query.all()
	return jsonify([user.serialize for user in users])# 모든 사용자정보 반환
	# res_users = {}
	# for user in users:# 반복문을 돌면서 직렬화된 변수를 넣어서 새로운 리스트를 만든다.
	#     res_users.append(user.serialize)
	# return jsonify(res_users)

# 주의 : primary 키인 id가 아니라 userid를 uri로 받음..
# 아이디 삭제, 수정, id(primary key)값에 따른 정보확인
@api.route('/users/<userid>', methods=['GET','PUT','DELETE'])
@jwt_required
def user_detail(userid):
	# 토큰을 가지고 들어오면 해당 토큰의 userid가 접근하려는 정보의 userid값과 같은지를 확인
	check_user_token = get_jwt_identity()
	if check_user_token != userid: # 들어온 토큰의 userid와 확인하려는 user의 id값이 다르면, 정보 확인 거절 -> 즉 다른 사용자가 다른 사용자의 userid를 확인하려는 경우
			return "Not your information"# 같지 않은 경우 접근금지

	if request.method == 'GET':# 아이디 정보 확인
		user = User.query.filter(User.userid == userid).first()
		return jsonify(user.serialize)

	elif request.method == 'DELETE':# 삭제
		db.session.query(User).filter(User.userid == userid).delete()
		db.session.commit()
		return jsonify("delete_success")# 204s는 상태 콜
		
	# 밑에 코드의 method는 'PUT'으로 아이디 수정

	data = request.get_json()# POST형식에 경우 form형식으로 데이터를 전달하지만 api호출할 때처럼 json데이터를 전달할 때는 form에 데이터가 없으므로 다른 방식을 써야한다.

	username = data.get('username')
	password = data.get('password')
	nickname = data.get('nickname')
	email = data.get('email')
	birth = data.get('birth')
	profile_img = request.files['profile_img']		# 프로필 사진 받아도 되고 안받아도 됨

	dt = datetime.strptime(birth, "%Y-%m-%d")# json형식으로 받은 data를 날짜 형식으로 변환

	updated_data = {}
	if username:# 바꿀 username을 입력받으면
		updated_data['username'] = username
	if password:# 바꿀 password를 입력받으면
		updated_data['password'] = password
	if nickname:# 바꿀 nickname을 입력받으면
		updated_data['nickname'] = nickname
	if email:# 바꿀 email를 입력받으면
		updated_data['email'] = email
	if birth:# 바꿀 생년월일을 입력받으면
		updated_data['birth'] = dt
	
	# 프로필 사진 이름 유저 테이블에 삽입 및 저장
	if profile_img and allowed_file(profile_img):		# 프로필 이미지 확장자 확인
		suffix = datetime.now().strftime("%y%m%d_%H%M%S")				
		filename = "_".join([profile_img.filename.rsplit('.', 1)[0], suffix])			# 중복된 이름의 사진을 받기위해서 파일명에 시간을 붙임
		extension = profile_img.filename.rsplit('.', 1)[1]
		filename = secure_filename(f"{filename}.{extension}")

		updated_data['profile_img'] = filename
		profile_img.save(os.path.join(UPLOAD_FOLDER,filename))

	User.query.filter(User.userid == userid).update(updated_data)# PUT은 전체를 업데이트할 때 사용하지만 일부 업데이트도 가능은함
	user = User.query.filter(User.userid == userid).first()
	return jsonify(user.serialize)


# 자동로그인을 할지 안할지를 반환
# 인자로 자동로그인을 할 떄는 1 아닐 때는 0을 반환해주어야 한다.
@api.route('/auto_login/<int:auto_login>') # methods가 아무것도 안적혀 있을 때는 GET으로 설정되어있음
@jwt_required
def auto_login():
    check_user= get_jwt_identity()
    access_user = User.query.filter(User.userid == check_user).first()# 꺼낸 토큰이 유효한 토큰인지 확인
    if access_user is None:
        return "User only"
    # 1아니면 0 값을 보내야하는데 다른 값을 보내는 경우 오류
    if auto_login != 1 or auto_login != 0:
        return "Wrong Value of auto_login"

    access_user.auto_login = auto_login
    result = access_user.auto_login
    return jsonify(
        result = result
    )


# userid로 프로필, 닉네임, 이메일(특정정보) 불러오는 api
@api.route('/user_specific_info/<userid>')
def users_specific_info(userid):
	user = User.query.filter(User.userid == userid).first()
	if user is None:
		print("없는 아이디입니다.")
		return "없는 아이디"
	user_specific_info = {
		'nickname' : user.nickname,
		'profile_img' : user.profile_img,
		'email' : user.email
	}
	return jsonify(user_specific_info)
