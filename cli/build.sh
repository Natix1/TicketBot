mkdir -p dist

echo "Installing go packages..."
go mod tidy

echo Building go static executable...

go build -o fileserver ./gosrc
mv fileserver ./dist

echo "Initializing virtual environment..."
python3 -m venv .venv

echo "Installing python dependencies..."
./.venv/bin/pip3 install -r requirements.txt

echo "Creating transcripts directory..."
mkdir -p transcripts

echo "Done!"
