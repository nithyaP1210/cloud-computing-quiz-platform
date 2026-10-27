# Cloud Quiz

A small serverless quiz app on AWS. Take a 5-question quiz, save your score, see the leaderboard.

## Architecture

```
Browser -> API Gateway (HTTP API) -> Lambda -> DynamoDB
```

| Part | Role |
|---|---|
| API Gateway | Public HTTPS endpoint |
| Lambda (`src/app.py`) | Serves the quiz page, saves scores (`POST /scores`), returns top 10 (`GET /scores`) |
| DynamoDB | Stores name, score, timestamp |
| CloudFormation (`template.yaml`) | Creates all of the above in one step |

## Deploy (AWS CloudShell, about 5 minutes)

1. Open **CloudShell** in the AWS Console.
2. Upload this folder as a zip (Actions > Upload file) and unzip it, or `git clone` your repo.
3. Run:
   ```bash
   cd cloud-quiz
   ./deploy.sh
   ```
4. Open the URL printed at the end.

## Clean up

```bash
./destroy.sh
```

## Project structure

```
cloud-quiz/
  template.yaml   infrastructure (DynamoDB, Lambda, API)
  deploy.sh       one-command deploy
  destroy.sh      one-command cleanup
  src/app.py      backend
  src/index.html  frontend
```
