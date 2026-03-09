document.addEventListener('DOMContentLoaded', () => {

    // 1. UIテキストと質問文の翻訳を定義
    const translations = {
        'ja': {
            'title': 'Label Me!',
            'description': 'いくつかの質問に答えて、<br>あなただけのオリジナルラベルを生成します。',
            'nickname_placeholder': 'ニックネームを入力',
            'start_btn': 'はじめる',
            'loading_text': 'あなたのラベルを生成中...',
            'restart_btn': 'もう一度試す',
            'nickname_alert': 'ニックネームを入力してください。',
            'nickname_alert_alphabet': 'ニックネームは半角アルファベットで入力してください。',
            // ▼▼▼ 追加 ▼▼▼
            'print_wait_text': '印刷完了までお待ちください',
            // ▲▲▲
            'questions': [
                // (質問は変更なし)
                {"text": "あなたは計画を立ててから\n行動する方ですか？", "type": "personality", "yes_text": "はい", "no_text": "いいえ"},
                {"text": "活気ある社交の場よりも、\n静かな一人の時間を好みますか？", "type": "personality", "yes_text": "はい", "no_text": "いいえ"},
                {"text": "注目を浴びるよりも\n陰で支える方が好きですか？", "type": "personality", "yes_text": "はい", "no_text": "いいえ"},
                {"text": "物事を決める時、\n感情よりも論理を優先しますか？", "type": "personality", "yes_text": "はい", "no_text": "いいえ"},
                {"text": "説明を受ける時、全体像（なぜ）よりも、\n具体的な手順（どうやるか）を先に知りたいですか？", "type": "personality", "yes_text": "はい", "no_text": "いいえ"},
                {"text": "決まったルーティンを守るよりも、\n新しいことを試すのが好きですか？", "type": "personality", "yes_text": "はい", "no_text": "いいえ"}
            ]
        },
        'en': {
            'title': 'Label Me!',
            'description': 'Answer a few questions to generate<br>your one-of-a-kind original label.',
            'nickname_placeholder': 'Enter your nickname',
            'start_btn': 'Start',
            'loading_text': 'Generating your label...',
            'restart_btn': 'Try Again',
            'nickname_alert': 'Please enter a nickname.',
            'nickname_alert_alphabet': 'Nickname must be alphabet characters only.',
            // ▼▼▼ 追加 ▼▼▼
            'print_wait_text': 'Please wait until printing is complete',
            // ▲▲▲
            'questions': [
                // (質問は変更なし)
                {"text": "Do you prefer to plan things out\nbefore taking action?", "type": "personality", "yes_text": "Yes", "no_text": "No"},
                {"text": "Do you prefer quiet time alone\nover lively social gatherings?", "type": "personality", "yes_text": "Yes", "no_text": "No"},
                {"text": "Do you prefer supporting from the sidelines\nrather than being in the spotlight?", "type": "personality", "yes_text": "Yes", "no_text": "No"},
                {"text": "When making decisions,\ndo you prioritize logic over emotion?", "type": "personality", "yes_text": "Yes", "no_text": "No"},
                {"text": "When getting instructions, do you prefer to know\nthe specific steps (how) before the big picture (why)?", "type": "personality", "yes_text": "Yes", "no_text": "No"},
                {"text": "Do you prefer trying new things\nover sticking to a set routine?", "type": "personality", "yes_text": "Yes", "no_text": "No"}
            ]
        }
    };

    // 2. DOM要素の取得
    const startContainer = document.getElementById('start-container');
    const quizContainer = document.getElementById('quiz-container');
    const loadingContainer = document.getElementById('loading-container');
    const resultContainer = document.getElementById('result-container');
    
    const questionText = document.getElementById('question-text');
    const yesBtn = document.getElementById('yes-btn');
    const noBtn = document.getElementById('no-btn');
    const resultImage = document.getElementById('result-image');
    const restartBtn = document.getElementById('restart-btn');
    const startBtn = document.getElementById('start-btn');
    const nicknameInput = document.getElementById('nickname-input');

    // UIテキスト用
    const uiTitle = document.getElementById('ui-title');
    const uiDescription = document.getElementById('ui-description');
    const uiLoadingText = document.getElementById('ui-loading-text');
    // ▼▼▼ 追加 ▼▼▼
    const uiPrintWaitText = document.getElementById('ui-print-wait-text');
    // ▲▲▲

    // 言語ボタン
    const langBtnJa = document.getElementById('lang-btn-ja');
    const langBtnEn = document.getElementById('lang-btn-en');

    // 3. 状態変数 (変更なし)
    let currentQuestionIndex = 0;
    let currentLang = 'ja'; 
    let user_data = { "lang": currentLang, "nickname": "", "explicit": [], "implicit": [] };
    let startTime;
    
    // 4. UI更新関数
    function updateUIText(lang) {
        currentLang = lang;
        user_data.lang = lang; 

        const t = translations[lang];

        langBtnJa.classList.toggle('active', lang === 'ja');
        langBtnEn.classList.toggle('active', lang === 'en');

        document.documentElement.lang = lang;

        // スタート画面
        uiTitle.textContent = t.title;
        uiDescription.innerHTML = t.description; 
        nicknameInput.placeholder = t.nickname_placeholder;
        startBtn.textContent = t.start_btn;

        // ローディング画面
        uiLoadingText.textContent = t.loading_text;

        // 結果画面
        restartBtn.textContent = t.restart_btn;
        // ▼▼▼ 追加 ▼▼▼
        uiPrintWaitText.textContent = t.print_wait_text;
        // ▲▲▲
    }

    // 5. 言語ボタンのイベントリスナー (変更なし)
    langBtnJa.addEventListener('click', () => updateUIText('ja'));
    langBtnEn.addEventListener('click', () => updateUIText('en'));


    // (startBtn.addEventListener ... 以下の残りのコードは変更なし)
    startBtn.addEventListener('click', () => {
        const nickname = nicknameInput.value.trim();
        
        if (nickname === "") {
            alert(translations[currentLang].nickname_alert);
            return;
        }
        
        const alphabetRegex = /^[a-zA-Z]+$/;
        if (!alphabetRegex.test(nickname)) {
            alert(translations[currentLang].nickname_alert_alphabet);
            return;
        }
        
        user_data.nickname = nickname;

        startContainer.classList.add('hidden');
        quizContainer.classList.remove('hidden');
        showQuestion();
    });

    function showQuestion() {
        const questions = translations[currentLang].questions; 
        
        if (currentQuestionIndex < questions.length) {
            const currentQuestion = questions[currentQuestionIndex];
            questionText.textContent = currentQuestion.text;
            yesBtn.textContent = currentQuestion.yes_text;
            noBtn.textContent = currentQuestion.no_text;
            startTime = Date.now();
        } else {
            finalize();
        }
    }

    function recordAnswer(answer) {
        const responseTime = (Date.now() - startTime) / 1000;
        
        const questions = translations[currentLang].questions; 
        const currentQuestion = questions[currentQuestionIndex];
        
        user_data.explicit.push({ 
            "question": currentQuestionIndex, 
            "answer": answer,
            "type": currentQuestion.type 
        });
        user_data.implicit.push({ 
            "question": currentQuestionIndex, 
            "time": responseTime,
            "type": currentQuestion.type
        });
        
        currentQuestionIndex++;
        showQuestion();
    }

    async function finalize() {
        quizContainer.classList.add('hidden');
        loadingContainer.classList.remove('hidden');

        try {
            const response = await fetch('/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(user_data),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'サーバーでエラーが発生しました。');
            }

            const imageBlob = await response.blob();
            resultImage.src = URL.createObjectURL(imageBlob);

            loadingContainer.classList.add('hidden');
            resultContainer.classList.remove('hidden');

        } catch (error) {
            console.error('Error:', error);
            const errorMsg = currentLang === 'en' ? 'An error occurred' : 'エラーが発生しました';
            loadingContainer.innerHTML = `<p>${errorMsg}: ${error.message}</p>`;
        }
    }

    yesBtn.addEventListener('click', () => recordAnswer('yes'));
    noBtn.addEventListener('click', () => recordAnswer('no'));
    restartBtn.addEventListener('click', () => {
        window.location.reload();
    });

    updateUIText(currentLang);
});