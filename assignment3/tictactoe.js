Vue.createApp({
    data() {
        return {
            board: [
                ['', '', ''],
                ['', '', ''],
                ['', '', '']
            ],
            currentPlayer: 'X',
            winner: null,
            isTie: false
        };
    },
    methods: {
        makeMove(row, col) {
            if (!this.board[row][col] && !this.winner) {
                this.board[row][col] = this.currentPlayer;
                if (this.checkWin()) {
                    this.winner = this.currentPlayer;
                } else if (this.checkTie()) {
                    this.isTie = true;
                } else {
                    this.currentPlayer = this.currentPlayer === 'X' ? 'O' : 'X';
                    if (this.currentPlayer === 'O') {
                        this.makeAIMove();
                    }
                }
            }
        },
        
        checkWin() {
            const lines = [
                [[0, 0], [0, 1], [0, 2]],
                [[1, 0], [1, 1], [1, 2]],
                [[2, 0], [2, 1], [2, 2]],

                [[0, 0], [1, 0], [2, 0]],
                [[0, 1], [1, 1], [2, 1]],
                [[0, 2], [1, 2], [2, 2]],

                [[0, 0], [1, 1], [2, 2]],
                [[0, 2], [1, 1], [2, 0]]
            ];
        
            for (let line of lines) {
                const [c1, c2, c3] = line;
                if (this.board[c1[0]][c1[1]] !== '' &&
                    this.board[c1[0]][c1[1]] === this.board[c2[0]][c2[1]] &&
                    this.board[c1[0]][c1[1]] === this.board[c3[0]][c3[1]]) {
                    return this.board[c1[0]][c1[1]];
                }
            }
        
            return null;
        },
        checkTie() {
            for (let i = 0; i < 3; i++) {
                for (let j = 0; j < 3; j++) {
                  if (!this.board[i][j]) {
                    return false;
                  }
                }
              }
              return true;
        },
        reset() {
            this.board = [
                ['', '', ''],
                ['', '', ''],
                ['', '', '']
            ];
            this.currentPlayer = 'X';
            this.winner = null;
            this.isTie = false;
        },
        makeAIMove() {
            let bestScore = -Infinity;
            let move = { i: -1, j: -1 };
        
            for (let i = 0; i < 3; i++) {
                for (let j = 0; j < 3; j++) {
                    if (this.board[i][j] === '') {
                        this.board[i][j] = 'O';
                        let score = this.minimax(this.board, 0, false);
                        this.board[i][j] = '';
        
                        if (score > bestScore) {
                            bestScore = score;
                            move = { i, j };
                        }
                    }
                }
            }
        
            if (move.i !== -1 && move.j !== -1) {
                this.board[move.i][move.j] = 'O';
                this.currentPlayer = 'X'; 
            }
            
            if (move.i !== -1 && move.j !== -1) {
                this.board[move.i][move.j] = 'O';
                if (this.checkWin()) {
                    this.winner = 'O';
                }
                this.currentPlayer = 'X'; 
            }

        },
        
        
        minimax(board, depth, isMaximizing) {
            let winner = this.checkWin();
            if (winner === 'O') return 10 - depth; 
            if (winner === 'X') return depth - 10; 
            if (this.checkTie()) return 0;
        
            if (isMaximizing) {
                let bestScore = -Infinity;
                for (let i = 0; i < 3; i++) {
                    for (let j = 0; j < 3; j++) {
                        if (board[i][j] === '') {
                            board[i][j] = 'O';
                            let score = this.minimax(board, depth + 1, false);
                            board[i][j] = '';
                            bestScore = Math.max(score, bestScore);
                        }
                    }
                }
                return bestScore;
            } else {
                let bestScore = Infinity;
                for (let i = 0; i < 3; i++) {
                    for (let j = 0; j < 3; j++) {
                        if (board[i][j] === '') {
                            board[i][j] = 'X';
                            let score = this.minimax(board, depth + 1, true);
                            board[i][j] = '';
                            bestScore = Math.min(score, bestScore);
                        }
                    }
                }
                return bestScore;
            }
        }
        
    }
}).mount('#app');