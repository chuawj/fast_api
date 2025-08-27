// frontend/script.js

const API_BASE_URL = 'http://127.0.0.1:8000';

function displayMessage(msg, type) {
    const messageDiv = document.getElementById('message');
    if (messageDiv) {
        messageDiv.textContent = msg;
        messageDiv.className = '';
        if (type) {
            messageDiv.classList.add(type);
        }
    } else {
        console.log(`Message (${type}): ${msg}`);
    }
}

let verifiedUserId = null;

function formatBirthDateToISO(dateString) {
    if (!dateString) return null;
    dateString = dateString.trim();

    const numericOnly = dateString.replace(/\D/g, '');

    if (/^\d{8}$/.test(numericOnly)) {
        const year = numericOnly.substring(0, 4);
        const month = numericOnly.substring(4, 6);
        const day = numericOnly.substring(6, 8);
        const isoFormatted = `${year}-${month}-${day}`;
        const dateObj = new Date(year, parseInt(month, 10) - 1, parseInt(day, 10));
        if (dateObj.getFullYear() === parseInt(year, 10) && dateObj.getMonth() === parseInt(month, 10) - 1 && dateObj.getDate() === parseInt(day, 10)) {
             return isoFormatted;
        } else {
             return null;
        }
    }

    const parts = dateString.replace(/[.\/]/g, '-').split('-');

    if (parts.length === 3) {
        const year = parts[0];
        const month = parts[1].padStart(2, '0');
        const day = parts[2].padStart(2, '0');

        if (year.length === 4 && month.length === 2 && day.length === 2) {
             const isoFormatted = `${year}-${month}-${day}`;
              const dateObj = new Date(year, parseInt(month, 10) - 1, parseInt(day, 10));
              if (dateObj.getFullYear() === parseInt(year, 10) && dateObj.getMonth() === parseInt(month, 10) - 1 && dateObj.getDate() === parseInt(day, 10)) {
                  return isoFormatted;
              } else {
                  return null;
              }
        }
    }

    return null;
}


document.addEventListener('DOMContentLoaded', () => {

    const signupForm = document.getElementById('signupForm');
    if (signupForm) {
        signupForm.addEventListener('submit', async (event) => {
            event.preventDefault();

            const username = document.getElementById('signupUsername').value;
            const email = document.getElementById('signupEmail').value;
            const password = document.getElementById('signupPassword').value;
            const phoneNumber = document.getElementById('signupPhoneNumber').value;
            const rawBirthDate = document.getElementById('signupBirthDate').value;

            const birthDate = formatBirthDateToISO(rawBirthDate);

            if (!birthDate) {
                displayMessage('생년월일을 YYYY-MM-DD 형식으로 올바르게 입력해주세요 (예: 2000-01-01).', 'error');
                return;
            }

            const signupData = {
                username: username,
                email: email,
                password: password,
                phone_number: phoneNumber,
                birth_date: birthDate
            };

            displayMessage('회원가입 처리 중...', '');

            try {
                const response = await fetch(`${API_BASE_URL}/signup/`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(signupData)
                });

                const result = await response.json();

                if (response.ok) {
                    displayMessage(`회원가입 성공! 사용자 ID: ${result.id}, 이름: ${result.username}`, 'success');
                    signupForm.reset();
                } else {
                    displayMessage(`회원가입 실패: ${result.detail || '알 수 없는 오류'}`, 'error');
                }
            } catch (error) {
                console.error('회원가입 요청 중 오류 발생:', error);
                displayMessage('회원가입 요청 중 오류가 발생했습니다. 서버 상태를 확인해주세요.', 'error');
            }
        });
    }

    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', async (event) => {
            event.preventDefault();

            const usernameInput = document.getElementById('loginUsername').value;
            const passwordInput = document.getElementById('loginPassword').value;

            const formData = new URLSearchParams();
            formData.append('username', usernameInput);
            formData.append('password', passwordInput);

            displayMessage('로그인 처리 중...', '');

            try {
                const response = await fetch(`${API_BASE_URL}/login/`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                    body: formData
                });

                const result = await response.json();

                if (response.ok) {
                    displayMessage(`로그인 성공: ${result.message}`, 'success');
                    loginForm.reset();
                } else {
                    displayMessage(`로그인 실패: ${result.detail || '알 수 없는 오류'}`, 'error');
                }
            } catch (error) {
                console.error('로그인 요청 중 오류 발생:', error);
                displayMessage('로그인 요청 중 오류가 발생했습니다. 서버 상태를 확인해주세요.', 'error');
            }
        });
    }

    const findUsernameForm = document.getElementById('findUsernameForm');
    if (findUsernameForm) {
         findUsernameForm.addEventListener('submit', async function(event) {
            event.preventDefault();

            const phoneNumber = document.getElementById('find_phone_number').value;
            const rawBirthDate = document.getElementById('find_birth_date').value;

            const birthDate = formatBirthDateToISO(rawBirthDate);

            if (!phoneNumber && !birthDate) {
                 displayMessage('전화번호와 생년월일을 모두 입력해주세요.', 'error');
                 return;
            }
             if (!birthDate) {
                 displayMessage('생년월일을 YYYY-MM-DD 형식으로 올바르게 입력해주세요 (예: 2000-01-01).', 'error');
                 return;
            }

            const findData = {
                phone_number: phoneNumber,
                birth_date: birthDate
            };

            displayMessage('아이디 찾는 중...', '');

            try {
                const response = await fetch(`${API_BASE_URL}/find-username/`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(findData)
                });

                const result = await response.json();

                if (response.ok) {
                    displayMessage(`찾으시는 아이디는: ${result.username} 입니다.`, 'success');
                } else {
                    displayMessage(`아이디 찾기 실패: ${result.detail || '정보와 일치하는 사용자가 없습니다.'}`, 'error');
                }
            } catch (error) {
                console.error('아이디 찾기 요청 중 오류 발생:', error);
                displayMessage('아이디 찾기 요청 중 오류가 발생했습니다. 서버 상태를 확인해주세요.', 'error');
            }
        });
    }
    const togglePasswordButtons = document.querySelectorAll('.toggle-password');
    togglePasswordButtons.forEach(button => {
        button.addEventListener('click', () => {
            const targetInputId = button.dataset.target;
            const passwordInput = document.getElementById(targetInputId);

            if (!passwordInput) {
                 console.error(`Password input with ID "${targetInputId}" not found.`);
                 return;
            }
            const currentType = passwordInput.getAttribute('type');

            const newType = currentType === 'password' ? 'text' : 'password';
            passwordInput.setAttribute('type', newType);

            button.textContent = newType === 'password' ? '보기' : '숨기기';
        });
    });
    const changePasswordForm = document.getElementById('changePasswordForm');
    const identityVerificationSection = document.getElementById('identity-verification-section');
    const passwordChangeSection = document.getElementById('password-change-section');
    const verifyIdentityButton = document.getElementById('verifyIdentityButton');

    const verifyUsernameInput = document.getElementById('verify_username');
    const verifyPhoneNumberInput = document.getElementById('verify_phone_number');
    const verifyBirthDateInput = document.getElementById('verify_birth_date');

    const newPasswordInput = document.getElementById('new_password');
    const confirmPasswordInput = document.getElementById('confirm_password');


    function setSectionRequired(section, isRequired) {
         if (section === identityVerificationSection) {
             if (verifyUsernameInput) { isRequired ? verifyUsernameInput.setAttribute('required', '') : verifyUsernameInput.removeAttribute('required'); }
             if (verifyPhoneNumberInput) { isRequired ? verifyPhoneNumberInput.setAttribute('required', '') : verifyPhoneNumberInput.removeAttribute('required'); }
             if (verifyBirthDateInput) { isRequired ? verifyBirthDateInput.setAttribute('required', '') : verifyBirthDateInput.removeAttribute('required'); }
         }
         else if (section === passwordChangeSection) {
             if (newPasswordInput) { isRequired ? newPasswordInput.setAttribute('required', '') : newPasswordInput.removeAttribute('required'); }
             if (confirmPasswordInput) { isRequired ? confirmPasswordInput.setAttribute('required', '') : confirmPasswordInput.removeAttribute('required'); }
         }
    }

    if (changePasswordForm && identityVerificationSection && passwordChangeSection && verifyIdentityButton && verifyBirthDateInput && newPasswordInput) {

        passwordChangeSection.style.display = 'none';
        setSectionRequired(passwordChangeSection, false);

        identityVerificationSection.style.display = 'block';
        setSectionRequired(identityVerificationSection, true);


        verifyIdentityButton.addEventListener('click', async function(event) {
            event.preventDefault();

            const username = verifyUsernameInput.value;
            const phoneNumber = verifyPhoneNumberInput.value;
            const rawBirthDate = verifyBirthDateInput.value;

            const birthDate = formatBirthDateToISO(rawBirthDate);

            if (!birthDate || (!username && !phoneNumber)) {
                 displayMessage('아이디(또는 이메일) 또는 전화번호 중 하나와 생년월일을 YYYY-MM-DD 형식으로 올바르게 입력해주세요.', 'error');
                 return;
            }

            setSectionRequired(identityVerificationSection, false);

            const verificationData = {
                username: username || null,
                phone_number: phoneNumber || null,
                birth_date: birthDate
            };

            displayMessage('본인 확인 중...', '');

            try {
                const response = await fetch(`${API_BASE_URL}/verify-identity-for-pw-change/`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(verificationData)
                });

                const result = await response.json();

                if (response.ok) {
                    displayMessage(result.message, 'success');
                    verifiedUserId = result.user_id;

                    identityVerificationSection.style.display = 'none';
                    setSectionRequired(identityVerificationSection, false);

                    passwordChangeSection.style.display = 'block';
                    setSectionRequired(passwordChangeSection, true);

                    if (verifyUsernameInput) verifyUsernameInput.value = '';
                    if (verifyPhoneNumberInput) verifyPhoneNumberInput.value = '';
                    if (verifyBirthDateInput) verifyBirthDateInput.value = '';

                } else {
                    displayMessage(`본인 확인 실패: ${result.detail || '정보와 일치하는 사용자를 찾을 수 없습니다.'}`, 'error');
                    verifiedUserId = null;
                    setSectionRequired(identityVerificationSection, true);
                    setSectionRequired(passwordChangeSection, false);
                }
            } catch (error) {
                console.error('본인 확인 요청 중 오류 발생:', error);
                displayMessage('본인 확인 요청 중 오류가 발생했습니다. 서버 상태를 확인해주세요.', 'error');
                verifiedUserId = null;
                setSectionRequired(identityVerificationSection, true);
                setSectionRequired(passwordChangeSection, false);
            }
        });

         changePasswordForm.addEventListener('submit', async function(event) {
             event.preventDefault();

             const newPassword = newPasswordInput.value;

             if (verifiedUserId === null) {
                 displayMessage('먼저 본인 확인을 해주세요.', 'error');
                 setSectionRequired(identityVerificationSection, true);
                 setSectionRequired(passwordChangeSection, false);
                 return;
             }

             if (!newPassword) {
                 displayMessage('새 비밀번호를 입력해주세요.', 'error');
                 setSectionRequired(identityVerificationSection, false);
                 setSectionRequired(passwordChangeSection, true);
                 return;
             }

             // TODO: 클라이언트 측 추가 비밀번호 유효성 검사 (예: 최소 길이, 문자 조합, 확인 필드 일치 등)
             // if (newPassword.length < 8) {
             //     displayMessage('비밀번호는 8자 이상이어야 합니다.', 'error');
             //     return;
             // }
             // if (confirmPassword && newPassword !== confirmPassword) {
             //      displayMessage('새 비밀번호와 비밀번호 확인이 일치하지 않습니다.', 'error');
             //      return;
             // }


            const changeData = {
                user_id: verifiedUserId,
                new_password: newPassword
            };

            displayMessage('비밀번호 변경 처리 중...', '');

            try {
                const response = await fetch(`${API_BASE_URL}/change-password-by-id/`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(changeData)
                });

                const result = await response.json();

                if (response.ok) {
                    displayMessage(`비밀번호 변경 성공: ${result.message}`, 'success');
                    changePasswordForm.reset();

                    verifiedUserId = null;

                    identityVerificationSection.style.display = 'block';
                    passwordChangeSection.style.display = 'none';

                    setSectionRequired(identityVerificationSection, true);
                    setSectionRequired(passwordChangeSection, false);

                } else {
                    displayMessage(`비밀번호 변경 실패: ${result.detail || '오류 발생'}`, 'error');
                    setSectionRequired(identityVerificationSection, false);
                    setSectionRequired(passwordChangeSection, true);
                }
            } catch (error) {
                console.error('비밀번호 변경 요청 중 오류 발생:', error);
                displayMessage('비밀번호 변경 요청 중 오류가 발생했습니다. 서버 상태를 확인해주세요.', 'error');
                setSectionRequired(identityVerificationSection, false);
                setSectionRequired(passwordChangeSection, true);
            }
         });
    }
});
