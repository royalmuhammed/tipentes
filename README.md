# 🛡️ LogicBreaker: AI-Powered Business Logic Scanner

> **Google Gemini Developer Competition 2026 Entry**
> *Automated Red Teaming using Multimodal AI Analysis*

## 💡 The Problem
Traditional security scanners (like ZAP or Burp Suite) are great at finding **technical bugs** (SQL Injection, XSS). However, they fail at finding **Business Logic Flaws**—bugs that require understanding *how* a human uses the application.

* *Example:* A user sees a price of $100 in the video, but modifies the API request to pay $1. A standard scanner doesn't know the price *should* be $100.

## 🚀 The Solution: LogicBreaker
LogicBreaker uses **Google Gemini 1.5 Flash (Multimodal)** to bridge this gap.
1.  **Visual Context:** It watches a video of the user's intended action (the "Happy Path").
2.  **Network Reality:** It analyzes the raw network logs (HAR files) generated during that session.
3.  **Logic Gap Detection:** It compares the two streams to identify discrepancies, IDORs, and workflow bypasses.

## 🛠️ Tech Stack
* **AI Core:** Google Gemini 1.5 Flash (via `google-genai` SDK)
* **Frontend:** Streamlit (Python)
* **Analysis:** Automated Video-to-Log correlation
* **Output:** JSON Vulnerability Reports + Auto-generated Python Exploit Scripts

## 📸 How to Run
1.  **Clone the Repo:**
    ```bash
    git clone [https://github.com/YOUR_USERNAME/LogicBreaker.git](https://github.com/YOUR_USERNAME/LogicBreaker.git)
    cd LogicBreaker
    ```

2.  **Install Dependencies:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    pip install -r requirements.txt
    ```

3.  **Set API Key:**
    Open `src/logic_engine.py` and add your Google Gemini API Key.

4.  **Launch the Dashboard:**
    ```bash
    streamlit run src/app.py
    ```
    *Credentials: judge / gemini2026*

## 🏆 Proof of Concept
Tested against **OWASP Juice Shop**.
* **Scenario:** Insecure Direct Object Reference (IDOR) in Review Submission.
* **Detection:** LogicBreaker successfully identified that the `UserId` parameter could be tampered with to impersonate the Admin.
* **Result:** Automatically generated a Python script to exploit the flaw.
