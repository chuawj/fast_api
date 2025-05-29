// frontend/script.js

// 백엔드 FastAPI 서버 주소
const API_BASE_URL = 'http://127.0.0.1:8000'; // Uvicorn 기본 주소

// 메시지 출력 함수
function displayMessage(msg, type) {
    const messageDiv = document.getElementById('message');
    if (messageDiv) { // 메시지 영역이 현재 페이지에 있는지 확인
        messageDiv.textContent = msg;
        messageDiv.className = ''; // 기존 클래스 초기화
        messageDiv.classList.add(type); // 'success' 또는 'error' 클래스 추가
    } else {
        console.log(`Message (${type}): ${msg}`); // 메시지 영역이 없으면 콘솔에 출력
    }
}

// DOMContentLoaded 이벤트: HTML 문서가 완전히 로드 및 파싱된 후 실행
document.addEventListener('DOMContentLoaded', () => {
    // 회원가입 폼 처리 (signup.html 페이지에서만 동작)
    const signupForm = document.getElementById('signupForm');
    if (signupForm) { // signupForm 요소가 현재 페이지에 있는지 확인
        signupForm.addEventListener('submit', async (event) => {
            event.preventDefault(); // 기본 제출 동작 방지

            const username = document.getElementById('signupUsername').value;
            const email = document.getElementById('signupEmail').value;
            const password = document.getElementById('signupPassword').value;

            const signupData = {
                username: username,
                email: email,
                password: password
            };

            try {
                const response = await fetch(`${API_BASE_URL}/signup/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(signupData)
                });

                if (response.ok) {
                    const data = await response.json();
                    displayMessage(`회원가입 성공! 사용자 ID: ${data.id}, 이름: ${data.username}`, 'success');
                    signupForm.reset(); // 폼 초기화
                    // 회원가입 성공 후 로그인 페이지로 이동 등의 로직 추가 가능
                    // setTimeout(() => { window.location.href = 'login.html'; }, 2000);
                } else {
                    const errorData = await response.json();
                    displayMessage(`회원가입 실패: ${errorData.detail}`, 'error');
                }
            } catch (error) {
                console.error('회원가입 요청 중 오류 발생:', error);
                displayMessage('회원가입 요청 중 오류가 발생했습니다.', 'error');
            }
        });
    }

    // 로그인 폼 처리 (login.html 페이지에서만 동작)
    const loginForm = document.getElementById('loginForm');
    if (loginForm) { // loginForm 요소가 현재 페이지에 있는지 확인
        loginForm.addEventListener('submit', async (event) => {
            event.preventDefault(); // 기본 제출 동작 방지

            const usernameInput = document.getElementById('loginUsername').value;
            const passwordInput = document.getElementById('loginPassword').value;

            const loginData = new URLSearchParams();
            loginData.append('username', usernameInput); // OAuth2Form 필드 이름
            loginData.append('password', passwordInput); // OAuth2Form 필드 이름

            try {
                const response = await fetch(`${API_BASE_URL}/login/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded'
                    },
                    body: loginData
                });

                if (response.ok) {
                    const data = await response.json();
                    displayMessage(`로그인 성공: ${data.message}`, 'success');
                    loginForm.reset(); // 폼 초기화
                    // 로그인 성공 후 메인 페이지 등으로 이동하는 로직 추가 가능
                } else {
                    const errorData = await response.json();
                    displayMessage(`로그인 실패: ${errorData.detail}`, 'error');
                }
            } catch (error) {
                console.error('로그인 요청 중 오류 발생:', error);
                displayMessage('로그인 요청 중 오류가 발생했습니다.', 'error');
            }
        });
    }
});

