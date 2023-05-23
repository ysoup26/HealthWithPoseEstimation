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

/*참고블로그: https://curryyou.tistory.com/447*/
const $video_user = document.querySelector("#video_user");
const $video_professor = document.querySelector("#video_professor");
const $video_record = document.querySelector("#video_record");

const $btn_start = document.querySelector('#btn_start');
const $btn_pause = document.querySelector('#btn_pause');
const $btn_resume = document.querySelector('#btn_resume');
const $btn_stop = document.querySelector('#btn_stop');
const countdown = document.querySelector("#countdown");
const countdownContainer = document.querySelector("#countdownContainer");

const arrVideoData = [];

let mediaStream,mediaRecorder;
let isRecording = false;

const pattern = /\/(\w+)\.mp4$/;
const match = $video_professor.src.match(pattern);
const professor_video_name = match && match[1];
//console.log("extractedString:", extractedString);

//User cam view start
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

// MediaRecorder set
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
    
        // BlobURL(ObjectURL) 생성
        const blobURL = window.URL.createObjectURL(videoBlob);
    
        // 녹화된 영상 재생: 두번째 video태그에서 재생
        $video_record.src = blobURL;
        $video_record.play();
        
        //window.location.href = '/health_do/health_report';
        const formData = new FormData();

    // Blob 데이터를 FormData에 추가
        formData.append('video', videoBlob, 'user.mp4');
        formData.append('professor_video_name',professor_video_name);
        
        // 서버로 데이터 전송
        fetch('/health_do/upload/', {
            method: 'POST',
            body: formData,
            headers:{
            'X-CSRFToken': csrftoken
            }
        })
        .then(response => response.json())
        .then(data => {
            const bad_body_part = data.compare_result; // 응답 데이터의 추가 데이터 추출
            window.location.href = '/health_do/health_report?bad_body_part=' + bad_body_part; 
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

// 녹화 종료 이벤트 - 최종에선 필요하지 않지만, 오류 체크를 위한 기능
$btn_stop.onclick = (event)=>{
    console.log("녹화종료")
    mediaRecorder.stop();
}
$video_professor.onended = (event)=>{
    console.log("녹화종료")
    mediaRecorder.stop();
}



