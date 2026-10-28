# EKI Worker test environment on WSL/Docker

WSL Ubuntu-22.04のDocker engineで、EKIのAgent/Worker test profileをビルド・試験する参照環境です。

**Taskを実行するWorkerではありません。** EKI Agentのclaim deliveryとWorker planeのtest profileを動かし、実行可能なバイナリを作るところまでを確認します。

## 前提

- WSL Ubuntu-22.04
- Docker 28.3.3
- EKI sourceをWSLのext4へ配置（`/mnt/d`はI/Oが遅いため使わない）

```text
mkdir -p /home/hat47x/eki-worker
# Windows側から cmd/, internal/, spec/, conformance/, go.mod, go.sum をコピー
```

## 実行

```text
chmod +x run.sh build.sh
EKI_ROOT=/home/hat47x/eki-worker ./run.sh
EKI_ROOT=/home/hat47x/eki-worker ./build.sh
```

## 確認したこと

- `go test ./internal/agent/... ./internal/control/... -count=1` がPASS。
- `eki-control`と`eki-agent`をLinux向けにビルドできる。
- `eki-control --version`と`eki-agent --version`が`dev`を返す。
- `smoke.sh`でControl Planeバイナリを起動し、`GET /v1/tasks`が405を返す。

証拠: [EKI-worker-env-2026-10-28.json](../../evaluations/records/EKI-worker-env-2026-10-28.json)

## 限界

- EKI Agentはclaim deliveryのtest profileであり、Taskの実行主体ではない。
- Task結果の受領・検証・委任完了は未確認。
- Worker認証、実Provider、実データ、Authorityは未検証。
- Docker test環境の成功を、実運用のWorker実行の成功へ読み替えない。
