/* Death Cafe 공통 스크립트
   ------------------------------------------------------------
   API_URL: 구글 Apps Script 웹앱 주소를 넣으면 게시판·신청서·자료실이
   실제로 저장됩니다. 비어 있는 동안은 예시 데이터로 "시범 운영" 됩니다. */
var DC = (function(){
  "use strict";
  var CONFIG = {
    API_URL: "https://script.google.com/macros/s/AKfycbwiy7sHsNyb04euHdOEkIgh1njshACJ3gBec9FS9ulEDRzSLIdl62Rmdp7pWh2Gbh-T/exec",
    EMAIL: "emilcha2@naver.com",
    BRUNCH: "https://brunch.co.kr/@ujuboygpqn?tab=works",
    YOUTUBE: "https://www.youtube.com/@spiritcare139"
  };
  var FIELDS = ["왜 죽음학인가","죽음과 죽어감","생애말기와 연명의료","죽음준비"];

  function esc(s){return String(s==null?"":s).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c];});}
  function today(){return new Date().toLocaleDateString('ko-KR');}
  var HEART = '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 21s-7.5-4.6-9.6-9.2C.9 8.4 3 4.5 6.8 4.5c2.1 0 3.6 1.1 4.3 2.3h1.8c.7-1.2 2.2-2.3 4.3-2.3 3.8 0 5.9 3.9 4.4 7.3C19.5 16.4 12 21 12 21z"/></svg>';

  /* ---------- 머리글·바닥글 ---------- */
  function chrome(current){
    var menu = [["about.html","소개"],["library.html","자료실"],["thoughts.html","생각 나누기"],["lecture.html","강의 신청"]];
    var nav = menu.map(function(m){return '<a href="'+m[0]+'"'+(m[0]===current?' aria-current="page"':'')+'>'+m[1]+'</a>';}).join('');
    var head = document.getElementById('site-header');
    if(head && !CONFIG.API_URL) head.insertAdjacentHTML('beforebegin','<p class="pilot">시범 운영 중입니다. 지금 보이는 글과 자료는 예시이며, 새로 남긴 글은 저장되지 않습니다.</p>');
    if(head) head.innerHTML =
      '<div class="site-header"><div class="wrap nav"><a class="logo" href="index.html"><span class="en">Death Cafe</span><span class="ko">데스카페</span></a><nav class="site-nav" aria-label="주 메뉴">'+nav+'</nav></div></div>';
    var foot = document.getElementById('site-footer');
    if(foot) foot.innerHTML =
      '<div class="site-footer"><div class="wrap"><div class="foot"><span>© Death Cafe 데스카페 · 차준택 (Spirit Care) · '+CONFIG.EMAIL+'</span>'+
      '<span class="links"><a href="'+CONFIG.BRUNCH+'" target="_blank" rel="noopener">브런치</a><a href="'+CONFIG.YOUTUBE+'" target="_blank" rel="noopener">유튜브</a></span></div>'+
      '<p class="care">마음이 많이 힘드시다면 혼자 견디지 마세요. 자살예방 상담전화 109 (24시간)</p>'+
      '<p class="care" style="opacity:.7">이 사이트는 방문 통계를 위해 Google 애널리틱스(쿠키)를 사용합니다. 개인을 식별하는 정보는 수집하지 않습니다.</p></div></div>';
  }

  /* ---------- 예시 데이터 (API_URL이 비어 있을 때만 사용) ---------- */
  var sample = {
    posts: [
      {id:"p3",name:"봄비",date:"2026. 9. 24.",vis:"public",likes:12,body:"아버지 마지막 한 달 동안 병원에서 '괜찮아질 거예요'라는 말만 했습니다. 정말 하고 싶었던 말은 '고마웠어요'였는데요. 그 말을 못 한 게 3년이 지나도 마음에 남아 있습니다.",_pw:""},
      {id:"p2",name:"어느 방문자",date:"2026. 9. 21.",vis:"private",likes:0,body:"",_body:"(나만 보기 예시 글입니다. 비밀번호 1234로 열 수 있습니다.)",_pw:"1234"},
      {id:"p1",name:"김정숙",date:"2026. 9. 18.",vis:"public",likes:7,body:"강의를 듣고 사전연명의료의향서를 처음 알았습니다. 다음 달에 남편과 같이 등록하러 가기로 했어요. 막상 이야기를 꺼내니 생각보다 담담했습니다.",_pw:""}
    ],
    library: [
      {id:"l1",f:0,type:"글",date:"2026. 10. 2.",title:"메멘토 모리, 아모르 파티, 카르페 디엠",sum:"죽음을 기억하는 일이 왜 오늘을 더 잘 사는 힘이 되는지, 세 개의 라틴어 문장으로 풀어봅니다.",body:"죽음을 생각하면 사람의 마음은 착해집니다.\n\n메멘토 모리는 죽음을 기억하라는 말입니다. 아모르 파티는 내게 주어진 운명을 사랑하라는 말이고, 카르페 디엠은 오늘을 붙잡으라는 말입니다.\n\n(예시 본문입니다.)",likes:14,comments:[{name:"하늘",date:"2026. 10. 3.",text:"마지막 문장이 오래 남네요."}]},
      {id:"l2",f:0,type:"강의자료",date:"2026. 10. 5.",title:"왜 죽음학인가: 강의 발췌본",sum:"1차시 강의자료 중 핵심 장면을 추려 PDF로 정리했습니다.",body:"죽음학이 무엇을 공부하는 학문인지, 왜 지금 우리에게 필요한지를 다룬 1차시 강의자료의 발췌본입니다. 전체 강의는 강의 신청 메뉴에서 문의해 주세요.",file:"",fileName:"왜죽음학인가_발췌본.pdf",likes:6,comments:[]},
      {id:"l3",f:1,type:"영상",date:"2026. 10. 8.",title:"영화로 풀어가는 웰다잉 이야기",sum:"영화 속 장면으로 죽어감과 이별을 이야기하는 유튜브 시리즈입니다.",body:"영화 한 편에서 시작하는 죽음과 삶에 대한 이야기입니다.",video:"https://www.youtube.com/@spiritcare139",likes:9,comments:[]},
      {id:"l4",f:1,type:"글",date:"2026. 10. 12.",title:"사별 후 애도는 어떻게 흘러가는가",sum:"사랑하는 사람을 잃은 뒤 겪는 마음의 변화와, 곁에 있는 사람이 할 수 있는 일.",body:"애도에는 정해진 순서가 없습니다. 슬픔은 파도처럼 밀려왔다가 물러나기를 반복합니다.\n\n(예시 본문입니다.)",likes:11,comments:[]},
      {id:"l5",f:2,type:"소식",date:"2026. 10. 15.",title:"사전연명의료의향서, 어디서 어떻게 작성하나요",sum:"등록기관 찾기부터 작성 절차까지 공식 안내 페이지를 소개합니다.",body:"사전연명의료의향서는 19세 이상이면 누구나 지정된 등록기관에서 작성할 수 있습니다. 가까운 등록기관과 절차는 국립연명의료관리기관 누리집에서 확인할 수 있습니다.\n\n(예시 본문입니다. 실제 게시 전 최신 정보를 확인해 주세요.)",link:"https://www.lst.go.kr",linkLabel:"국립연명의료관리기관 바로가기",likes:21,comments:[]},
      {id:"l6",f:3,type:"강의자료",date:"2026. 10. 22.",title:"나의 죽음준비계획서 (인쇄용 양식)",sum:"손으로 직접 쓰며 삶을 정리해 보는 죽음준비계획서 양식입니다.",body:"감사한 순간, 남은 삶의 소망, 연명의료에 대한 생각, 장례에 대한 바람, 남기고 싶은 말을 차례로 적어 보는 양식입니다. 개인의 생각을 정리하기 위한 것으로 법적 효력은 없습니다.",file:"",fileName:"나의_죽음준비계획서.pdf",likes:17,comments:[]}
    ]
  };
  var n = 100;
  function find(list,id){for(var i=0;i<list.length;i++){if(list[i].id===id)return list[i];}return null;}
  function publicPost(p){return {id:p.id,name:p.name,date:p.date,vis:p.vis,likes:p.likes,body:p.vis==="public"?p.body:""};}

  function local(action, d){
    var P = sample.posts, L = sample.library, x;
    switch(action){
      case "listPosts": return {ok:true, items:P.map(publicPost)};
      case "addPost":
        x={id:"p"+(n++),name:d.name,date:today(),vis:d.vis,likes:0,body:d.vis==="public"?d.body:"",_body:d.body,_pw:d.pw};
        P.unshift(x); return {ok:true, item:publicPost(x)};
      case "unlockPost": x=find(P,d.id); return (x && x._pw && x._pw===d.pw) ? {ok:true, body:x._body||x.body} : {ok:false, error:"비밀번호가 맞지 않습니다."};
      case "deletePost": x=find(P,d.id); if(!x||!x._pw||x._pw!==d.pw) return {ok:false, error:"비밀번호가 맞지 않습니다."}; sample.posts=P.filter(function(p){return p.id!==d.id;}); return {ok:true};
      case "like": x=find(d.kind==="post"?P:L,d.id); if(x){x.likes=Math.max(0,x.likes+(d.delta>0?1:-1));} return {ok:true, likes:x?x.likes:0};
      case "listLibrary": return {ok:true, items:L};
      case "addComment": x=find(L,d.id); x.comments.push({name:d.name,date:today(),text:d.text}); return {ok:true, comments:x.comments};
      case "lecture": return {ok:true};
    }
    return {ok:false, error:"알 수 없는 요청입니다."};
  }

  function api(action, data){
    data = data || {};
    if(!CONFIG.API_URL) return Promise.resolve(local(action, data));
    var body = JSON.stringify(Object.assign({action:action}, data));
    return fetch(CONFIG.API_URL, {method:"POST", headers:{"Content-Type":"text/plain;charset=utf-8"}, body:body})
      .then(function(r){return r.json();})
      .catch(function(){return {ok:false, error:"연결이 원활하지 않습니다. 잠시 후 다시 시도해 주세요."};});
  }

  /* 공감: 같은 브라우저에서 한 번만 누르도록 기억 */
  function likedKey(kind,id){return "dc_like_"+kind+"_"+id;}
  function isLiked(kind,id){try{return localStorage.getItem(likedKey(kind,id))==="1";}catch(e){return false;}}
  function setLiked(kind,id,v){try{v?localStorage.setItem(likedKey(kind,id),"1"):localStorage.removeItem(likedKey(kind,id));}catch(e){}}

  return {CONFIG:CONFIG, FIELDS:FIELDS, esc:esc, HEART:HEART, chrome:chrome, api:api, isLiked:isLiked, setLiked:setLiked};
})();
