/* 자료실 개별 페이지(library/<id>.html): 공감 수·댓글을 최신 상태로 불러오고 댓글을 받습니다.
   본문은 tools/build.py가 미리 써 둔 HTML이라 검색엔진이 그대로 읽습니다. */
(function(){
  "use strict";
  DC.chrome("library.html");
  var art=document.getElementById('libItem'); if(!art) return;
  var id=art.dataset.id, esc=DC.esc, x=null;
  var like=document.getElementById('like'), box=document.getElementById('comments');

  function renderComments(){
    var cm=(x&&x.comments)||[];
    box.innerHTML='<h2>댓글 '+cm.length+'</h2>'
      +cm.map(function(c){return '<div class="cmt"><span class="who">'+esc(c.name)+'<span>'+esc(c.date)+'</span></span><p>'+esc(c.text)+'</p></div>';}).join('')
      +'<form class="cform" id="cform" novalidate><input type="text" id="cn" maxlength="20" placeholder="닉네임" aria-label="닉네임"><input type="password" id="cp" maxlength="20" placeholder="비밀번호 (삭제용)" aria-label="비밀번호"><textarea id="ct" maxlength="500" rows="3" placeholder="자료를 보고 느낀 점을 남겨주세요." aria-label="댓글 내용"></textarea><div class="foot"><p class="err" id="cerr" hidden></p><span></span><button type="submit" class="btn btn-primary">댓글 남기기</button></div></form>';
    document.getElementById('cform').onsubmit=function(e){
      e.preventDefault();
      var n=document.getElementById('cn').value.trim(),p=document.getElementById('cp').value,t=document.getElementById('ct').value.trim(),er=document.getElementById('cerr');
      var pr=!n?'닉네임을 입력해 주세요.':p.length<4?'비밀번호를 4자 이상 입력해 주세요.':!t?'댓글 내용을 입력해 주세요.':'';
      if(pr){er.textContent=pr;er.hidden=false;return;}
      DC.api("addComment",{id:id,name:n,pw:p,text:t}).then(function(r){
        if(!r.ok){er.textContent=r.error;er.hidden=false;return;}
        x.comments=r.comments;renderComments();
      });
    };
  }

  like.setAttribute('aria-pressed',DC.isLiked('lib',id));
  like.onclick=function(){
    if(!x) return;
    var on=!DC.isLiked('lib',id);DC.setLiked('lib',id,on);
    x.likes=Math.max(0,(+x.likes||0)+(on?1:-1));
    like.setAttribute('aria-pressed',on);like.querySelector('span').textContent=x.likes;
    DC.api("like",{kind:"lib",id:id,delta:on?1:-1});
  };

  DC.api("listLibrary").then(function(r){
    x=(r.items||[]).filter(function(i){return i.id===id;})[0]||{id:id,likes:0,comments:[]};
    like.querySelector('span').textContent=x.likes||0;
    renderComments();
  });
})();
