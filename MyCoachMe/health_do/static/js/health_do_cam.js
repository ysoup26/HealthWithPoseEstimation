//django의 csrf 제한을 풀기 위한 부분.
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
const csrftoken = getCookie('csrftoken');


//비디오
const $video_user = document.querySelector("#video_user");
const $video_professor = document.querySelector("#video_professor");
//운동 버튼
const $btn_start = document.querySelector('#btn_start');
const $btn_pause = document.querySelector('#btn_pause');    //제외가능
const $btn_resume = document.querySelector('#btn_resume');  //제외가능
const $btn_stop = document.querySelector('#btn_stop');
//운동 시작 직후 카운트 다운
const countdown = document.querySelector("#countdown");
const countdownContainer = document.querySelector("#countdownContainer");
//로딩
const loading = document.querySelector("#loading");

const arrVideoData = [];

let mediaStream,mediaRecorder;
let isRecording = false;

//비디오 파일로부터 비디오 이름만 추출하기 위한 부분(운동 비교시 필요)
const pattern = /\/(\w+)\.mp4$/;
const match = $video_professor.src.match(pattern);
const professor_video_name = match && match[1];

//캠화면 시작
if (navigator.mediaDevices.getUserMedia) {
    navigator.mediaDevices.getUserMedia({ video: true })
      .then(function (stream) {
        $video_user.srcObject = stream;
        mediaStream = stream
        setupMediaRecorder();
      })
      .catch(function (err0r) {
        console.log("Something went wrong!");
      });
}

//레코더 설정
function setupMediaRecorder() {
    mediaRecorder = new MediaRecorder(mediaStream);
    
    //arrVideoData 배열에 녹화 데이터를 담음
    mediaRecorder.ondataavailable = (event) => {
      arrVideoData.push(event.data);
    }
  
    mediaRecorder.onstop = (event) => {
       // 배열에 담아둔 녹화 데이터들을 통합한 Blob객체 생성
        const videoBlob = new Blob(arrVideoData);
    
        let filename = "user.mp4";
        const file = new File([videoBlob], filename);
        console.log(videoBlob)
    
        const formData = new FormData();

        //POST를 위한 Form 데이터
        formData.append('video', videoBlob, 'user.mp4');
        formData.append('professor_video_name',professor_video_name);
        
        /*로딩창 관련부분(임시)*/
        loading.style.display = "block";
        
        //서버로 데이터 전송 - 운동 비교를 위해
        fetch('/health_do/upload/', {
            method: 'POST',
            body: formData,
            headers:{
            'X-CSRFToken': csrftoken /*필수*/ 
            }
        })
        .then(response => response.json())
        .then(data => {
            //응답 받은 내용으로 리포트 페이지 실행
            const bad_body_part = data.compare_result; 
            window.location.href = '/health_do/health_report?bad_body_part=' + encodeURIComponent(bad_body_part); 
        })
        .catch(error => {
            console.log('에러 발생', error);
        });
      // 기존 녹화 데이터 제거
      arrVideoData.splice(0);
    }
}

function pauseMediaRecorder() {
    if (isRecording) {
      mediaRecorder.pause();
      isRecording = false;
    }
}
  
function resumeMediaRecorder() {
    if (!isRecording) {
      mediaRecorder.resume();
      isRecording = true;
    }
}
    
// 운동 시작 이벤트
//3초 동안 대기 후 -> 전문가 영상 시작, 녹화 시작
$btn_start.onclick = (event)=>{
    setupMediaRecorder();
    let count = 3;
    
    countdownContainer.style.display = "block";
    countdown.textContent = count;

    const countdownInterval = setInterval(()=>{
        count--;
        countdown.textContent = count;
        if( count == 0){
            clearInterval(countdownInterval);
            countdownContainer.style.display = "none";
            console.log("녹화시작")
            mediaRecorder.start(); // 3초 후에 녹화 시작
            console.log("운동시작")
            $video_professor.play();
            isRecording = true;
        }
    },1000);
}

//녹화 일시 정지 이벤트
$btn_pause.onclick = (event)=>{
    console.log("녹화 일시 정지")
    pauseMediaRecorder();
    $video_professor.pause();

}
// 녹화 다시 시작 이벤트
//+)다시 시작하기전 3초정도 대기해야함.
$btn_resume.onclick = (event) => {
    let count = 3;
    
    countdownContainer.style.display = "block";
    countdown.textContent = count;

    const countdownInterval = setInterval(()=>{
        count--;
        countdown.textContent = count;
        if( count == 0){
            clearInterval(countdownInterval);
            countdownContainer.style.display = "none";
            console.log("녹화 다시 시작");
            resumeMediaRecorder();
            $video_professor.play();
        }
    },1000);

    
};

// 전문가 영상 종료 이벤트
// 일단은 스탑 버튼을 누를 때와 영상이 종료되었을때 둘다 운동 비교를 하게함.
$btn_stop.onclick = (event)=>{
    console.log("녹화종료")
    mediaRecorder.stop();
}
$video_professor.onended = (event)=>{
    console.log("녹화종료")
    mediaRecorder.stop();
}



