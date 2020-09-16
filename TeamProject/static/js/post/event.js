
//===========보드 메인 포스트 페이지 ==========
function handle_goMain(){
  const board_id = location.hash.split('#')[1];
	location.href=`#${board_id}#postmain#1`; //페이지 이동
  // history.pushState(null, 'Go main', '/rooms/#');
  // router();

}

//===========보드 메인 포스트 인풋창  ==========
function handle_Input(){//인풋창
  const ele = document.querySelector('.input__off');
  ele.addEventListener('click',function(){
    input_post();
  });
}

function handle_inputOff(){
  render_inputOff();
  handle_Input();
}

function handle_submitPost(){//인풋창 submit

  const input = document.querySelector('.input_file');//파일 인풋 테그
  const preview = document.querySelector('.file_preview'); //파일 미리보기 태그
  const submit = document.getElementById('button_submit'); //파일 제출 버튼 태그  

  submit.addEventListener('click',submit_post); //버튼 json 제출 이벤트 리스너
 //  submit.addEventListener('click',function(){ // 파일 제출 이벤트 리스너 
 //   fetch_upload(input.files);
 // });
 //  input.addEventListener('change' , function(){//파일 미리보기 이벤트 리스너 
 //    const curfiles = input.files; //현재 선택된 파일
 //    paint_preview(curfiles, preview);
 //  });
}


//===========보드 Postinfo 페이지 ==========
function handle_postinfo(){//post info 창 페이지 이동
  const board_id = location.hash.split('#')[1];
  const event_id = event.currentTarget.id.split('__');
  location.href=`#${board_id}#postinfo#${event_id[1]}`; //페이지 이동
  // history.pushState(event_id[1], 'Go postinfo_', '/rooms/#postinfo');
  // router();
}

function handle_delete(){//post info삭제 
 const confirmflag = confirm("삭제하시겠습니까?");
 const post_id = location.hash.split('#')[3];
 if(confirmflag) delete_post(post_id);
}

function handle_update(){// post info수정 
  const event_id = event.currentTarget.id.split('__');
  update_post(event_id[1]);
}
submit_updatePost

//===========게시글 로딩 이벤트 ==========
function handle_scrollLoading(hashValue){
  window.addEventListener('scroll', () => {
  let scrollLocation = document.documentElement.scrollTop; // 현재 스크롤바 위치
  let windowHeight = window.innerHeight; // 스크린 창
  let fullHeight = document.body.scrollHeight; //  margin 값은 포함 x
  if(scrollLocation + windowHeight >= fullHeight){
   add_newPosts(hashValue);
  }
  this.removeEventListener("scroll",arguments.callee); //이벤트 제거 
});
}



//==========신고 이벤트===========//

function handle_report(){

}

function handle_likes(){

}

function handle_mail(){

}
function handle_commentInsert(){

}
function handle_commentDelete(){

}
function handle_commentUpdate(){

}
function handle_Commentlikes(){

}
function handle_Commentreport(){
  
}