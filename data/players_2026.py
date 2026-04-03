"""
실제 2025-26 시즌 주요 선수 데이터
2026년 3월 16일 기준 - 확장된 선수 명단
"""

# La Liga 주요 선수
LA_LIGA_PLAYERS = {
    "Barcelona": [
        # 공격수
        {"name": "Robert Lewandowski", "position": "FW", "age": 37, "rating": 8.5, "goals": 18, "assists": 5},
        {"name": "Lamine Yamal", "position": "RW", "age": 18, "rating": 8.3, "goals": 12, "assists": 10},
        {"name": "Marcus Rashford", "position": "FW", "age": 28, "rating": 7.9, "goals": 10, "assists": 4},
        {"name": "Ferran Torres", "position": "FW", "age": 25, "rating": 7.6, "goals": 8, "assists": 6},
        {"name": "Roony Bardghji", "position": "FW", "age": 20, "rating": 7.2, "goals": 2, "assists": 3},
        # 미드필더
        {"name": "Pedri", "position": "MF", "age": 23, "rating": 8.1, "goals": 5, "assists": 8},
        {"name": "Gavi", "position": "MF", "age": 21, "rating": 7.9, "goals": 4, "assists": 6},
        {"name": "Frenkie de Jong", "position": "MF", "age": 28, "rating": 7.8, "goals": 3, "assists": 7},
        {"name": "Fermín López", "position": "MF", "age": 22, "rating": 7.5, "goals": 6, "assists": 4},
        {"name": "Dani Olmo", "position": "MF", "age": 27, "rating": 7.7, "goals": 7, "assists": 5},
        # 수비수
        {"name": "Jules Koundé", "position": "CB", "age": 26, "rating": 7.9, "goals": 2, "assists": 1},
        {"name": "Ronald Araújo", "position": "CB", "age": 26, "rating": 7.8, "goals": 3, "assists": 0},
        {"name": "Pau Cubarsí", "position": "CB", "age": 18, "rating": 7.4, "goals": 1, "assists": 0},
        {"name": "Alejandro Balde", "position": "LB", "age": 22, "rating": 7.6, "goals": 1, "assists": 5},
        {"name": "Héctor Fort", "position": "RB", "age": 19, "rating": 7.2, "goals": 0, "assists": 2},
        # 골키퍼
        {"name": "Marc-André ter Stegen", "position": "GK", "age": 33, "rating": 7.8, "goals": 0, "assists": 0},
        {"name": "Iñaki Peña", "position": "GK", "age": 26, "rating": 7.1, "goals": 0, "assists": 0},
    ],
    "Real Madrid": [
        # 공격수
        {"name": "Kylian Mbappé", "position": "FW", "age": 27, "rating": 8.7, "goals": 20, "assists": 8},
        {"name": "Vinícius Júnior", "position": "LW", "age": 25, "rating": 8.6, "goals": 16, "assists": 9},
        {"name": "Rodrygo", "position": "RW", "age": 24, "rating": 7.9, "goals": 11, "assists": 7},
        {"name": "Arda Güler", "position": "FW", "age": 20, "rating": 7.7, "goals": 8, "assists": 5},
        {"name": "Gonzalo", "position": "FW", "age": 19, "rating": 7.3, "goals": 4, "assists": 2},
        # 미드필더
        {"name": "Jude Bellingham", "position": "MF", "age": 22, "rating": 8.4, "goals": 14, "assists": 7},
        {"name": "Federico Valverde", "position": "MF", "age": 26, "rating": 8.2, "goals": 9, "assists": 6},
        {"name": "Aurélien Tchouaméni", "position": "MF", "age": 25, "rating": 7.8, "goals": 2, "assists": 3},
        {"name": "Dani Ceballos", "position": "MF", "age": 29, "rating": 7.4, "goals": 3, "assists": 4},
        {"name": "Franco Mastantuono", "position": "MF", "age": 18, "rating": 7.2, "goals": 1, "assists": 2},
        # 수비수
        {"name": "Trent Alexander-Arnold", "position": "RB", "age": 27, "rating": 8.0, "goals": 2, "assists": 11},
        {"name": "Éder Militão", "position": "CB", "age": 27, "rating": 7.9, "goals": 3, "assists": 1},
        {"name": "David Alaba", "position": "CB", "age": 33, "rating": 7.7, "goals": 1, "assists": 2},
        {"name": "Dean Huijsen", "position": "CB", "age": 20, "rating": 7.3, "goals": 2, "assists": 0},
        {"name": "Álvaro Carreras", "position": "LB", "age": 22, "rating": 7.5, "goals": 1, "assists": 4},
        {"name": "Fran García", "position": "LB", "age": 25, "rating": 7.3, "goals": 0, "assists": 3},
        # 골키퍼
        {"name": "Thibaut Courtois", "position": "GK", "age": 33, "rating": 7.9, "goals": 0, "assists": 0},
        {"name": "Andriy Lunin", "position": "GK", "age": 26, "rating": 7.4, "goals": 0, "assists": 0},
    ],
    "Atletico Madrid": [
        {"name": "Antoine Griezmann", "position": "FW", "age": 34, "rating": 8.0, "goals": 12, "assists": 8},
        {"name": "Julián Álvarez", "position": "FW", "age": 25, "rating": 7.8, "goals": 10, "assists": 5},
        {"name": "Alexander Sørloth", "position": "FW", "age": 29, "rating": 7.6, "goals": 9, "assists": 3},
        {"name": "Rodrigo De Paul", "position": "MF", "age": 31, "rating": 7.5, "goals": 3, "assists": 6},
        {"name": "Marcos Llorente", "position": "MF", "age": 30, "rating": 7.6, "goals": 5, "assists": 4},
        {"name": "Koke", "position": "MF", "age": 33, "rating": 7.4, "goals": 2, "assists": 5},
        {"name": "José María Giménez", "position": "CB", "age": 30, "rating": 7.7, "goals": 2, "assists": 1},
        {"name": "Jan Oblak", "position": "GK", "age": 32, "rating": 8.1, "goals": 0, "assists": 0},
    ],
    "Villarreal": [
        {"name": "Ayoze Pérez", "position": "FW", "age": 32, "rating": 7.7, "goals": 11, "assists": 6},
        {"name": "Thierno Barry", "position": "FW", "age": 22, "rating": 7.5, "goals": 9, "assists": 4},
        {"name": "Álex Baena", "position": "MF", "age": 24, "rating": 7.8, "goals": 7, "assists": 8},
        {"name": "Dani Parejo", "position": "MF", "age": 36, "rating": 7.6, "goals": 3, "assists": 7},
        {"name": "Diego Conde", "position": "GK", "age": 26, "rating": 7.4, "goals": 0, "assists": 0},
    ],
    "Real Betis": [
        {"name": "Vitor Roque", "position": "FW", "age": 20, "rating": 7.6, "goals": 10, "assists": 3},
        {"name": "Giovani Lo Celso", "position": "MF", "age": 29, "rating": 7.7, "goals": 6, "assists": 7},
        {"name": "Nabil Fekir", "position": "MF", "age": 32, "rating": 7.5, "goals": 5, "assists": 6},
        {"name": "Marc Bartra", "position": "CB", "age": 34, "rating": 7.3, "goals": 2, "assists": 1},
        {"name": "Rui Silva", "position": "GK", "age": 31, "rating": 7.4, "goals": 0, "assists": 0},
    ]
}

# Bundesliga 주요 선수
BUNDESLIGA_PLAYERS = {
    "Bayern Munich": [
        # 공격수
        {"name": "Harry Kane", "position": "FW", "age": 32, "rating": 8.9, "goals": 30, "assists": 6},
        {"name": "Luis Díaz", "position": "FW", "age": 28, "rating": 8.3, "goals": 15, "assists": 13},
        {"name": "Michael Olise", "position": "FW", "age": 23, "rating": 8.1, "goals": 12, "assists": 17},
        {"name": "Mathys Tel", "position": "FW", "age": 20, "rating": 7.4, "goals": 6, "assists": 4},
        # 미드필더
        {"name": "Jamal Musiala", "position": "MF", "age": 22, "rating": 8.5, "goals": 11, "assists": 12},
        {"name": "Joshua Kimmich", "position": "MF", "age": 30, "rating": 8.2, "goals": 3, "assists": 10},
        {"name": "Leon Goretzka", "position": "MF", "age": 30, "rating": 7.7, "goals": 5, "assists": 6},
        {"name": "Konrad Laimer", "position": "MF", "age": 28, "rating": 7.5, "goals": 4, "assists": 5},
        {"name": "Aleksandar Pavlović", "position": "MF", "age": 21, "rating": 7.3, "goals": 2, "assists": 3},
        # 수비수
        {"name": "Alphonso Davies", "position": "LB", "age": 25, "rating": 7.9, "goals": 2, "assists": 8},
        {"name": "Dayot Upamecano", "position": "CB", "age": 26, "rating": 7.7, "goals": 3, "assists": 1},
        {"name": "Kim Min-jae", "position": "CB", "age": 28, "rating": 7.8, "goals": 1, "assists": 0},
        {"name": "Hiroki Ito", "position": "CB", "age": 26, "rating": 7.4, "goals": 1, "assists": 0},
        {"name": "Raphaël Guerreiro", "position": "LB", "age": 31, "rating": 7.5, "goals": 2, "assists": 7},
        # 골키퍼
        {"name": "Manuel Neuer", "position": "GK", "age": 39, "rating": 7.8, "goals": 0, "assists": 0},
        {"name": "Daniel Peretz", "position": "GK", "age": 24, "rating": 7.1, "goals": 0, "assists": 0},
    ],
    "Borussia Dortmund": [
        # 공격수
        {"name": "Serhou Guirassy", "position": "FW", "age": 29, "rating": 8.3, "goals": 18, "assists": 4},
        {"name": "Maximilian Beier", "position": "FW", "age": 22, "rating": 7.6, "goals": 9, "assists": 5},
        {"name": "Jamie Gittens", "position": "FW", "age": 21, "rating": 7.5, "goals": 7, "assists": 6},
        # 미드필더
        {"name": "Julian Brandt", "position": "MF", "age": 29, "rating": 7.9, "goals": 8, "assists": 11},
        {"name": "Marcel Sabitzer", "position": "MF", "age": 31, "rating": 7.7, "goals": 6, "assists": 7},
        {"name": "Felix Nmecha", "position": "MF", "age": 24, "rating": 7.4, "goals": 4, "assists": 5},
        {"name": "Pascal Groß", "position": "MF", "age": 34, "rating": 7.6, "goals": 3, "assists": 8},
        # 수비수
        {"name": "Nico Schlotterbeck", "position": "CB", "age": 25, "rating": 7.7, "goals": 2, "assists": 1},
        {"name": "Waldemar Anton", "position": "CB", "age": 28, "rating": 7.6, "goals": 1, "assists": 0},
        {"name": "Ramy Bensebaini", "position": "LB", "age": 30, "rating": 7.4, "goals": 2, "assists": 3},
        {"name": "Julian Ryerson", "position": "RB", "age": 27, "rating": 7.3, "goals": 1, "assists": 4},
        # 골키퍼
        {"name": "Gregor Kobel", "position": "GK", "age": 27, "rating": 7.8, "goals": 0, "assists": 0},
        {"name": "Alexander Meyer", "position": "GK", "age": 34, "rating": 7.0, "goals": 0, "assists": 0},
    ],
    "TSG Hoffenheim": [
        {"name": "Andrej Kramarić", "position": "FW", "age": 34, "rating": 7.8, "goals": 14, "assists": 7},
        {"name": "Marius Bülter", "position": "FW", "age": 32, "rating": 7.5, "goals": 10, "assists": 5},
        {"name": "Tom Bischof", "position": "MF", "age": 20, "rating": 7.6, "goals": 6, "assists": 8},
        {"name": "Anton Stach", "position": "MF", "age": 26, "rating": 7.4, "goals": 4, "assists": 6},
        {"name": "Oliver Baumann", "position": "GK", "age": 35, "rating": 7.5, "goals": 0, "assists": 0},
    ],
    "VfB Stuttgart": [
        {"name": "Ermedin Demirović", "position": "FW", "age": 27, "rating": 7.7, "goals": 12, "assists": 5},
        {"name": "Deniz Undav", "position": "FW", "age": 28, "rating": 7.6, "goals": 11, "assists": 6},
        {"name": "Enzo Millot", "position": "MF", "age": 23, "rating": 7.5, "goals": 7, "assists": 7},
        {"name": "Angelo Stiller", "position": "MF", "age": 24, "rating": 7.4, "goals": 3, "assists": 5},
        {"name": "Alexander Nübel", "position": "GK", "age": 28, "rating": 7.6, "goals": 0, "assists": 0},
    ],
    "RB Leipzig": [
        {"name": "Benjamin Šeško", "position": "FW", "age": 22, "rating": 7.9, "goals": 13, "assists": 4},
        {"name": "Loïs Openda", "position": "FW", "age": 25, "rating": 7.8, "goals": 12, "assists": 5},
        {"name": "Xavi Simons", "position": "MF", "age": 22, "rating": 7.7, "goals": 8, "assists": 9},
        {"name": "Amadou Haidara", "position": "MF", "age": 27, "rating": 7.4, "goals": 3, "assists": 4},
        {"name": "Péter Gulácsi", "position": "GK", "age": 35, "rating": 7.5, "goals": 0, "assists": 0},
    ],
    "Bayer Leverkusen": [
        {"name": "Victor Boniface", "position": "FW", "age": 24, "rating": 7.8, "goals": 11, "assists": 6},
        {"name": "Florian Wirtz", "position": "MF", "age": 22, "rating": 8.2, "goals": 9, "assists": 10},
        {"name": "Granit Xhaka", "position": "MF", "age": 32, "rating": 7.7, "goals": 4, "assists": 7},
        {"name": "Jonathan Tah", "position": "CB", "age": 29, "rating": 7.8, "goals": 3, "assists": 1},
        {"name": "Lukáš Hrádecký", "position": "GK", "age": 35, "rating": 7.6, "goals": 0, "assists": 0},
    ]
}

# Serie A 주요 선수
SERIE_A_PLAYERS = {
    "Inter Milan": [
        # 공격수
        {"name": "Lautaro Martínez", "position": "FW", "age": 27, "rating": 8.6, "goals": 22, "assists": 5},
        {"name": "Marcus Thuram", "position": "FW", "age": 27, "rating": 8.2, "goals": 16, "assists": 8},
        {"name": "Ange-Yoan Bonny", "position": "FW", "age": 22, "rating": 7.4, "goals": 7, "assists": 3},
        # 미드필더
        {"name": "Nicolò Barella", "position": "MF", "age": 28, "rating": 8.1, "goals": 6, "assists": 9},
        {"name": "Hakan Çalhanoğlu", "position": "MF", "age": 31, "rating": 7.9, "goals": 5, "assists": 7},
        {"name": "Henrikh Mkhitaryan", "position": "MF", "age": 36, "rating": 7.7, "goals": 4, "assists": 6},
        {"name": "Davide Frattesi", "position": "MF", "age": 25, "rating": 7.6, "goals": 7, "assists": 4},
        {"name": "Piotr Zieliński", "position": "MF", "age": 31, "rating": 7.5, "goals": 3, "assists": 5},
        {"name": "Petar Sučić", "position": "MF", "age": 22, "rating": 7.3, "goals": 2, "assists": 3},
        {"name": "Andy Diouf", "position": "MF", "age": 22, "rating": 7.2, "goals": 1, "assists": 2},
        # 수비수
        {"name": "Alessandro Bastoni", "position": "CB", "age": 26, "rating": 8.0, "goals": 3, "assists": 4},
        {"name": "Stefan de Vrij", "position": "CB", "age": 33, "rating": 7.7, "goals": 2, "assists": 1},
        {"name": "Francesco Acerbi", "position": "CB", "age": 37, "rating": 7.6, "goals": 1, "assists": 0},
        {"name": "Manuel Akanji", "position": "CB", "age": 30, "rating": 7.8, "goals": 2, "assists": 1},
        {"name": "Denzel Dumfries", "position": "RB", "age": 29, "rating": 7.7, "goals": 4, "assists": 5},
        {"name": "Federico Dimarco", "position": "LB", "age": 28, "rating": 7.8, "goals": 3, "assists": 7},
        {"name": "Matteo Darmian", "position": "RB", "age": 35, "rating": 7.3, "goals": 1, "assists": 2},
        {"name": "Carlos Augusto", "position": "LB", "age": 26, "rating": 7.4, "goals": 2, "assists": 3},
        # 골키퍼
        {"name": "Yann Sommer", "position": "GK", "age": 37, "rating": 7.7, "goals": 0, "assists": 0},
        {"name": "Josep Martínez", "position": "GK", "age": 27, "rating": 7.2, "goals": 0, "assists": 0},
    ],
    "AC Milan": [
        # 공격수
        {"name": "Rafael Leão", "position": "LW", "age": 25, "rating": 8.3, "goals": 14, "assists": 10},
        {"name": "Christian Pulisic", "position": "RW", "age": 27, "rating": 8.0, "goals": 11, "assists": 8},
        {"name": "Santiago Giménez", "position": "FW", "age": 24, "rating": 7.8, "goals": 13, "assists": 4},
        {"name": "Christopher Nkunku", "position": "FW", "age": 28, "rating": 7.7, "goals": 9, "assists": 6},
        # 미드필더
        {"name": "Luka Modrić", "position": "MF", "age": 40, "rating": 7.8, "goals": 3, "assists": 6},
        {"name": "Adrien Rabiot", "position": "MF", "age": 30, "rating": 7.7, "goals": 5, "assists": 5},
        {"name": "Youssouf Fofana", "position": "MF", "age": 26, "rating": 7.6, "goals": 4, "assists": 4},
        {"name": "Ruben Loftus-Cheek", "position": "MF", "age": 29, "rating": 7.4, "goals": 6, "assists": 3},
        {"name": "Samuele Ricci", "position": "MF", "age": 23, "rating": 7.5, "goals": 2, "assists": 5},
        # 수비수
        {"name": "Fikayo Tomori", "position": "CB", "age": 27, "rating": 7.7, "goals": 2, "assists": 1},
        {"name": "Matteo Gabbia", "position": "CB", "age": 25, "rating": 7.6, "goals": 3, "assists": 0},
        {"name": "Strahinja Pavlović", "position": "CB", "age": 24, "rating": 7.4, "goals": 1, "assists": 0},
        {"name": "Perr Estupiñán", "position": "LB", "age": 27, "rating": 7.5, "goals": 1, "assists": 4},
        {"name": "Alexis Saelemaekers", "position": "RB", "age": 26, "rating": 7.3, "goals": 2, "assists": 5},
        # 골키퍼
        {"name": "Mike Maignan", "position": "GK", "age": 29, "rating": 8.1, "goals": 0, "assists": 0},
        {"name": "Marco Sportiello", "position": "GK", "age": 33, "rating": 7.0, "goals": 0, "assists": 0},
    ],
    "Napoli": [
        # 공격수
        {"name": "Victor Osimhen", "position": "FW", "age": 26, "rating": 8.4, "goals": 19, "assists": 4},
        {"name": "Khvicha Kvaratskhelia", "position": "LW", "age": 24, "rating": 8.2, "goals": 13, "assists": 9},
        {"name": "Matteo Politano", "position": "RW", "age": 31, "rating": 7.6, "goals": 8, "assists": 7},
        {"name": "Giacomo Raspadori", "position": "FW", "age": 25, "rating": 7.4, "goals": 6, "assists": 4},
        # 미드필더
        {"name": "Stanislav Lobotka", "position": "MF", "age": 30, "rating": 7.7, "goals": 2, "assists": 5},
        {"name": "Frank Anguissa", "position": "MF", "age": 29, "rating": 7.6, "goals": 4, "assists": 3},
        {"name": "Piotr Zieliński", "position": "MF", "age": 31, "rating": 7.5, "goals": 5, "assists": 6},
        # 수비수
        {"name": "Amir Rrahmani", "position": "CB", "age": 31, "rating": 7.6, "goals": 3, "assists": 1},
        {"name": "Juan Jesus", "position": "CB", "age": 34, "rating": 7.3, "goals": 1, "assists": 0},
        {"name": "Mathías Olivera", "position": "LB", "age": 28, "rating": 7.4, "goals": 2, "assists": 3},
        {"name": "Giovanni Di Lorenzo", "position": "RB", "age": 32, "rating": 7.5, "goals": 3, "assists": 4},
        # 골키퍼
        {"name": "Alex Meret", "position": "GK", "age": 28, "rating": 7.6, "goals": 0, "assists": 0},
    ],
    "Como": [
        {"name": "Patrick Cutrone", "position": "FW", "age": 27, "rating": 7.7, "goals": 12, "assists": 5},
        {"name": "Nico Paz", "position": "MF", "age": 21, "rating": 7.6, "goals": 8, "assists": 7},
        {"name": "Alberto Dossena", "position": "CB", "age": 27, "rating": 7.4, "goals": 4, "assists": 2},
        {"name": "Emil Audero", "position": "GK", "age": 28, "rating": 7.5, "goals": 0, "assists": 0},
    ],
    "Juventus": [
        {"name": "Dušan Vlahović", "position": "FW", "age": 25, "rating": 8.0, "goals": 16, "assists": 4},
        {"name": "Kenan Yıldız", "position": "FW", "age": 20, "rating": 7.7, "goals": 9, "assists": 6},
        {"name": "Teun Koopmeiners", "position": "MF", "age": 27, "rating": 7.8, "goals": 7, "assists": 8},
        {"name": "Manuel Locatelli", "position": "MF", "age": 27, "rating": 7.5, "goals": 3, "assists": 5},
        {"name": "Federico Gatti", "position": "CB", "age": 27, "rating": 7.6, "goals": 4, "assists": 1},
        {"name": "Michele Di Gregorio", "position": "GK", "age": 28, "rating": 7.7, "goals": 0, "assists": 0},
    ]
}

# EPL 주요 선수
EPL_PLAYERS = {
    "Liverpool": [
        # 공격수
        {"name": "Mohamed Salah", "position": "RW", "age": 33, "rating": 8.8, "goals": 22, "assists": 14},
        {"name": "Alexander Isak", "position": "FW", "age": 25, "rating": 8.5, "goals": 18, "assists": 6},
        {"name": "Hugo Ekitike", "position": "FW", "age": 23, "rating": 7.8, "goals": 11, "assists": 5},
        {"name": "Cody Gakpo", "position": "LW", "age": 26, "rating": 7.7, "goals": 9, "assists": 7},
        {"name": "Luis Díaz", "position": "LW", "age": 28, "rating": 7.9, "goals": 10, "assists": 8},
        # 미드필더
        {"name": "Florian Wirtz", "position": "MF", "age": 22, "rating": 8.4, "goals": 12, "assists": 11},
        {"name": "Alexis Mac Allister", "position": "MF", "age": 26, "rating": 7.8, "goals": 5, "assists": 8},
        {"name": "Dominik Szoboszlai", "position": "MF", "age": 24, "rating": 7.7, "goals": 6, "assists": 7},
        {"name": "Ryan Gravenberch", "position": "MF", "age": 23, "rating": 7.6, "goals": 4, "assists": 5},
        # 수비수
        {"name": "Virgil van Dijk", "position": "CB", "age": 34, "rating": 8.2, "goals": 3, "assists": 2},
        {"name": "Ibrahima Konaté", "position": "CB", "age": 26, "rating": 7.8, "goals": 2, "assists": 1},
        {"name": "Andy Robertson", "position": "LB", "age": 31, "rating": 7.7, "goals": 1, "assists": 6},
        {"name": "Conor Bradley", "position": "RB", "age": 22, "rating": 7.5, "goals": 2, "assists": 4},
        # 골키퍼
        {"name": "Alisson Becker", "position": "GK", "age": 33, "rating": 8.0, "goals": 0, "assists": 0},
        {"name": "Giorgi Mamardashvili", "position": "GK", "age": 25, "rating": 7.4, "goals": 0, "assists": 0},
    ],
    "Arsenal": [
        # 공격수
        {"name": "Viktor Gyökeres", "position": "FW", "age": 26, "rating": 8.6, "goals": 24, "assists": 5},
        {"name": "Bukayo Saka", "position": "RW", "age": 24, "rating": 8.3, "goals": 13, "assists": 11},
        {"name": "Gabriel Martinelli", "position": "LW", "age": 24, "rating": 7.9, "goals": 10, "assists": 8},
        {"name": "Leandro Trossard", "position": "FW", "age": 30, "rating": 7.6, "goals": 8, "assists": 6},
        # 미드필더
        {"name": "Martin Zubimendi", "position": "MF", "age": 26, "rating": 8.1, "goals": 4, "assists": 7},
        {"name": "Declan Rice", "position": "MF", "age": 26, "rating": 8.0, "goals": 5, "assists": 8},
        {"name": "Martin Ødegaard", "position": "MF", "age": 26, "rating": 8.2, "goals": 9, "assists": 10},
        {"name": "Kai Havertz", "position": "MF", "age": 26, "rating": 7.7, "goals": 7, "assists": 5},
        # 수비수
        {"name": "William Saliba", "position": "CB", "age": 24, "rating": 8.2, "goals": 2, "assists": 1},
        {"name": "Gabriel Magalhães", "position": "CB", "age": 27, "rating": 8.0, "goals": 4, "assists": 2},
        {"name": "Ben White", "position": "RB", "age": 27, "rating": 7.8, "goals": 1, "assists": 4},
        {"name": "Jurriën Timber", "position": "LB", "age": 24, "rating": 7.6, "goals": 2, "assists": 3},
        # 골키퍼
        {"name": "David Raya", "position": "GK", "age": 29, "rating": 7.9, "goals": 0, "assists": 0},
    ],
    "Manchester City": [
        # 공격수
        {"name": "Erling Haaland", "position": "FW", "age": 25, "rating": 8.9, "goals": 26, "assists": 4},
        {"name": "Phil Foden", "position": "MF", "age": 25, "rating": 8.1, "goals": 11, "assists": 9},
        {"name": "Jack Grealish", "position": "LW", "age": 30, "rating": 7.7, "goals": 6, "assists": 8},
        {"name": "Jérémy Doku", "position": "RW", "age": 23, "rating": 7.6, "goals": 7, "assists": 6},
        # 미드필더
        {"name": "Kevin De Bruyne", "position": "MF", "age": 34, "rating": 8.3, "goals": 8, "assists": 15},
        {"name": "Rodri", "position": "MF", "age": 29, "rating": 8.4, "goals": 5, "assists": 7},
        {"name": "Bernardo Silva", "position": "MF", "age": 30, "rating": 8.0, "goals": 9, "assists": 10},
        {"name": "Mateo Kovačić", "position": "MF", "age": 31, "rating": 7.6, "goals": 3, "assists": 5},
        # 수비수
        {"name": "Rúben Dias", "position": "CB", "age": 28, "rating": 7.9, "goals": 1, "assists": 0},
        {"name": "John Stones", "position": "CB", "age": 31, "rating": 7.7, "goals": 2, "assists": 1},
        {"name": "Nathan Aké", "position": "LB", "age": 30, "rating": 7.5, "goals": 1, "assists": 2},
        {"name": "Kyle Walker", "position": "RB", "age": 35, "rating": 7.4, "goals": 0, "assists": 3},
        # 골키퍼
        {"name": "Gianluigi Donnarumma", "position": "GK", "age": 26, "rating": 8.0, "goals": 0, "assists": 0},
    ],
    "Chelsea": [
        {"name": "Cole Palmer", "position": "MF", "age": 23, "rating": 8.2, "goals": 15, "assists": 9},
        {"name": "Nicolas Jackson", "position": "FW", "age": 24, "rating": 7.7, "goals": 12, "assists": 5},
        {"name": "Enzo Fernández", "position": "MF", "age": 24, "rating": 7.8, "goals": 6, "assists": 7},
        {"name": "Moisés Caicedo", "position": "MF", "age": 24, "rating": 7.6, "goals": 4, "assists": 4},
        {"name": "Levi Colwill", "position": "CB", "age": 22, "rating": 7.7, "goals": 2, "assists": 1},
        {"name": "Robert Sánchez", "position": "GK", "age": 28, "rating": 7.3, "goals": 0, "assists": 0},
    ],
    "Tottenham": [
        {"name": "Richarlison", "position": "FW", "age": 28, "rating": 7.6, "goals": 10, "assists": 3},
        {"name": "Dominic Solanke", "position": "FW", "age": 28, "rating": 7.5, "goals": 8, "assists": 4},
        {"name": "Mathys Tel", "position": "FW", "age": 20, "rating": 7.4, "goals": 6, "assists": 5},
        {"name": "Mohammed Kudus", "position": "MF", "age": 25, "rating": 7.7, "goals": 7, "assists": 6},
        {"name": "Xavi Simons", "position": "MF", "age": 22, "rating": 7.9, "goals": 9, "assists": 8},
        {"name": "James Maddison", "position": "MF", "age": 28, "rating": 7.8, "goals": 6, "assists": 9},
        {"name": "Dejan Kulusevski", "position": "RW", "age": 25, "rating": 7.6, "goals": 7, "assists": 7},
        {"name": "Rodrigo Bentancur", "position": "MF", "age": 28, "rating": 7.3, "goals": 2, "assists": 4},
        {"name": "Pape Matar Sarr", "position": "MF", "age": 22, "rating": 7.2, "goals": 3, "assists": 3},
        {"name": "Conor Gallagher", "position": "MF", "age": 26, "rating": 7.5, "goals": 4, "assists": 5},
        {"name": "Cristian Romero", "position": "CB", "age": 27, "rating": 7.7, "goals": 2, "assists": 1},
        {"name": "Micky van de Ven", "position": "CB", "age": 24, "rating": 7.6, "goals": 4, "assists": 0},
        {"name": "Kevin Danso", "position": "CB", "age": 27, "rating": 7.4, "goals": 1, "assists": 0},
        {"name": "Ben Davies", "position": "LB", "age": 32, "rating": 7.1, "goals": 1, "assists": 2},
        {"name": "Guglielmo Vicario", "position": "GK", "age": 29, "rating": 7.3, "goals": 0, "assists": 0},
    ],
    "Manchester United": [
        {"name": "Rasmus Højlund", "position": "FW", "age": 22, "rating": 7.7, "goals": 11, "assists": 4},
        {"name": "Bruno Fernandes", "position": "MF", "age": 31, "rating": 8.0, "goals": 10, "assists": 11},
        {"name": "Marcus Rashford", "position": "LW", "age": 28, "rating": 7.6, "goals": 9, "assists": 5},
        {"name": "Kobbie Mainoo", "position": "MF", "age": 20, "rating": 7.5, "goals": 4, "assists": 6},
        {"name": "Lisandro Martínez", "position": "CB", "age": 27, "rating": 7.7, "goals": 2, "assists": 1},
        {"name": "André Onana", "position": "GK", "age": 29, "rating": 7.4, "goals": 0, "assists": 0},
    ],
    "Newcastle": [
        {"name": "Anthony Gordon", "position": "LW", "age": 24, "rating": 7.9, "goals": 12, "assists": 7},
        {"name": "Bruno Guimarães", "position": "MF", "age": 27, "rating": 8.0, "goals": 7, "assists": 8},
        {"name": "Sandro Tonali", "position": "MF", "age": 25, "rating": 7.7, "goals": 5, "assists": 6},
        {"name": "Sven Botman", "position": "CB", "age": 25, "rating": 7.6, "goals": 2, "assists": 1},
        {"name": "Nick Pope", "position": "GK", "age": 33, "rating": 7.6, "goals": 0, "assists": 0},
    ]
}

# NBA 주요 선수
NBA_PLAYERS = {
    "Boston Celtics": [
        {"name": "Jayson Tatum", "position": "F", "age": 27, "rating": 9.2, "ppg": 28.5, "rpg": 8.2, "apg": 5.1},
        {"name": "Jaylen Brown", "position": "G-F", "age": 28, "rating": 8.8, "ppg": 24.3, "rpg": 6.1, "apg": 4.2},
        {"name": "Kristaps Porziņģis", "position": "C", "age": 29, "rating": 8.3, "ppg": 19.8, "rpg": 7.5, "apg": 2.1},
        {"name": "Derrick White", "position": "G", "age": 31, "rating": 7.9, "ppg": 15.2, "rpg": 4.1, "apg": 5.3},
        {"name": "Jrue Holiday", "position": "G", "age": 35, "rating": 7.8, "ppg": 12.8, "rpg": 4.5, "apg": 6.2},
        {"name": "Al Horford", "position": "C", "age": 39, "rating": 7.4, "ppg": 8.5, "rpg": 6.8, "apg": 2.4},
        {"name": "Payton Pritchard", "position": "G", "age": 27, "rating": 7.3, "ppg": 10.2, "rpg": 2.8, "apg": 3.5},
        {"name": "Sam Hauser", "position": "F", "age": 27, "rating": 7.1, "ppg": 8.8, "rpg": 3.2, "apg": 1.1},
        {"name": "Luke Kornet", "position": "C", "age": 29, "rating": 6.9, "ppg": 5.2, "rpg": 4.1, "apg": 1.2},
        {"name": "Xavier Tillman", "position": "F-C", "age": 26, "rating": 6.8, "ppg": 4.5, "rpg": 3.8, "apg": 1.5},
        {"name": "Neemias Queta", "position": "C", "age": 25, "rating": 6.7, "ppg": 4.2, "rpg": 3.5, "apg": 0.5},
        {"name": "Jordan Walsh", "position": "F", "age": 21, "rating": 6.5, "ppg": 2.8, "rpg": 2.1, "apg": 0.8},
        {"name": "Jaden Springer", "position": "G", "age": 22, "rating": 6.4, "ppg": 2.5, "rpg": 1.5, "apg": 1.2},
    ],
    "Cleveland Cavaliers": [
        {"name": "Donovan Mitchell", "position": "G", "age": 29, "rating": 9.0, "ppg": 27.8, "rpg": 4.9, "apg": 6.1},
        {"name": "Darius Garland", "position": "G", "age": 25, "rating": 8.5, "ppg": 21.4, "rpg": 3.2, "apg": 7.8},
        {"name": "Evan Mobley", "position": "F-C", "age": 24, "rating": 8.4, "ppg": 18.6, "rpg": 9.3, "apg": 3.1},
        {"name": "Jarrett Allen", "position": "C", "age": 27, "rating": 8.1, "ppg": 14.2, "rpg": 10.5, "apg": 1.8},
        {"name": "Max Strus", "position": "F", "age": 29, "rating": 7.4, "ppg": 11.3, "rpg": 4.2, "apg": 2.9},
        {"name": "Caris LeVert", "position": "G", "age": 31, "rating": 7.3, "ppg": 10.8, "rpg": 3.5, "apg": 4.1},
        {"name": "Isaac Okoro", "position": "F", "age": 24, "rating": 7.1, "ppg": 9.2, "rpg": 3.1, "apg": 2.2},
        {"name": "Dean Wade", "position": "F", "age": 28, "rating": 6.9, "ppg": 6.5, "rpg": 3.8, "apg": 1.5},
        {"name": "Georges Niang", "position": "F", "age": 32, "rating": 6.8, "ppg": 5.8, "rpg": 2.5, "apg": 1.2},
        {"name": "Sam Merrill", "position": "G", "age": 29, "rating": 6.7, "ppg": 5.2, "rpg": 1.8, "apg": 1.5},
        {"name": "Ty Jerome", "position": "G", "age": 28, "rating": 6.6, "ppg": 4.8, "rpg": 1.5, "apg": 2.8},
        {"name": "Craig Porter Jr.", "position": "G", "age": 23, "rating": 6.4, "ppg": 3.2, "rpg": 1.2, "apg": 1.8},
    ],
    "New York Knicks": [
        {"name": "Jalen Brunson", "position": "G", "age": 28, "rating": 8.9, "ppg": 26.7, "rpg": 3.8, "apg": 7.5},
        {"name": "Karl-Anthony Towns", "position": "C", "age": 29, "rating": 8.6, "ppg": 24.1, "rpg": 11.2, "apg": 3.4},
        {"name": "Mikal Bridges", "position": "F", "age": 29, "rating": 8.2, "ppg": 18.5, "rpg": 5.1, "apg": 3.8},
        {"name": "OG Anunoby", "position": "F", "age": 28, "rating": 7.9, "ppg": 15.8, "rpg": 6.3, "apg": 2.1},
        {"name": "Josh Hart", "position": "F", "age": 30, "rating": 7.7, "ppg": 12.4, "rpg": 8.9, "apg": 4.6},
        {"name": "Donte DiVincenzo", "position": "G", "age": 28, "rating": 7.5, "ppg": 11.8, "rpg": 3.5, "apg": 3.2},
        {"name": "Miles McBride", "position": "G", "age": 25, "rating": 7.2, "ppg": 9.5, "rpg": 2.1, "apg": 3.8},
        {"name": "Precious Achiuwa", "position": "F-C", "age": 26, "rating": 7.0, "ppg": 7.8, "rpg": 6.2, "apg": 1.2},
        {"name": "Mitchell Robinson", "position": "C", "age": 27, "rating": 7.1, "ppg": 6.5, "rpg": 8.5, "apg": 0.8},
        {"name": "Cameron Payne", "position": "G", "age": 31, "rating": 6.8, "ppg": 5.2, "rpg": 1.8, "apg": 3.5},
        {"name": "Jericho Sims", "position": "C", "age": 26, "rating": 6.5, "ppg": 3.8, "rpg": 4.2, "apg": 0.5},
        {"name": "Tyler Kolek", "position": "G", "age": 24, "rating": 6.3, "ppg": 2.5, "rpg": 1.2, "apg": 2.1},
    ],
    "Milwaukee Bucks": [
        {"name": "Giannis Antetokounmpo", "position": "F", "age": 30, "rating": 9.5, "ppg": 30.2, "rpg": 11.8, "apg": 6.3},
        {"name": "Damian Lillard", "position": "G", "age": 35, "rating": 8.7, "ppg": 25.6, "rpg": 4.1, "apg": 7.9},
        {"name": "Khris Middleton", "position": "F", "age": 34, "rating": 7.8, "ppg": 16.3, "rpg": 5.2, "apg": 4.8},
        {"name": "Brook Lopez", "position": "C", "age": 37, "rating": 7.6, "ppg": 11.8, "rpg": 5.9, "apg": 1.4},
        {"name": "Bobby Portis", "position": "F-C", "age": 30, "rating": 7.4, "ppg": 13.5, "rpg": 7.8, "apg": 1.5},
        {"name": "Gary Trent Jr.", "position": "G", "age": 26, "rating": 7.2, "ppg": 10.8, "rpg": 2.5, "apg": 2.1},
        {"name": "Pat Connaughton", "position": "G-F", "age": 32, "rating": 6.9, "ppg": 7.2, "rpg": 3.8, "apg": 1.8},
        {"name": "AJ Green", "position": "G", "age": 25, "rating": 6.7, "ppg": 6.5, "rpg": 1.5, "apg": 1.2},
        {"name": "Taurean Prince", "position": "F", "age": 31, "rating": 6.8, "ppg": 5.8, "rpg": 3.2, "apg": 1.5},
        {"name": "Delon Wright", "position": "G", "age": 33, "rating": 6.6, "ppg": 4.5, "rpg": 2.1, "apg": 3.2},
        {"name": "MarJon Beauchamp", "position": "F", "age": 25, "rating": 6.4, "ppg": 3.8, "rpg": 2.5, "apg": 1.1},
        {"name": "Ryan Rollins", "position": "G", "age": 23, "rating": 6.2, "ppg": 2.5, "rpg": 1.2, "apg": 1.5},
    ],
    "Oklahoma City Thunder": [
        {"name": "Shai Gilgeous-Alexander", "position": "G", "age": 26, "rating": 9.4, "ppg": 31.2, "rpg": 5.8, "apg": 6.5},
        {"name": "Chet Holmgren", "position": "C", "age": 22, "rating": 8.6, "ppg": 18.4, "rpg": 9.2, "apg": 2.8},
        {"name": "Jalen Williams", "position": "F", "age": 23, "rating": 8.4, "ppg": 20.1, "rpg": 5.5, "apg": 4.9},
        {"name": "Lu Dort", "position": "G", "age": 26, "rating": 7.7, "ppg": 12.3, "rpg": 4.2, "apg": 2.1},
        {"name": "Isaiah Hartenstein", "position": "C", "age": 27, "rating": 7.8, "ppg": 10.5, "rpg": 9.8, "apg": 3.2},
        {"name": "Alex Caruso", "position": "G", "age": 31, "rating": 7.6, "ppg": 8.7, "rpg": 3.5, "apg": 3.8},
        {"name": "Aaron Wiggins", "position": "G-F", "age": 26, "rating": 7.1, "ppg": 9.2, "rpg": 3.1, "apg": 1.8},
        {"name": "Cason Wallace", "position": "G", "age": 21, "rating": 7.0, "ppg": 7.5, "rpg": 2.5, "apg": 2.8},
        {"name": "Isaiah Joe", "position": "G", "age": 26, "rating": 6.9, "ppg": 8.8, "rpg": 2.1, "apg": 1.5},
        {"name": "Ajay Mitchell", "position": "G", "age": 23, "rating": 6.6, "ppg": 5.2, "rpg": 1.8, "apg": 2.5},
        {"name": "Jaylin Williams", "position": "F-C", "age": 23, "rating": 6.5, "ppg": 4.5, "rpg": 3.8, "apg": 1.2},
        {"name": "Ousmane Dieng", "position": "F", "age": 22, "rating": 6.4, "ppg": 3.8, "rpg": 2.5, "apg": 1.5},
    ],
    "Denver Nuggets": [
        {"name": "Nikola Jokić", "position": "C", "age": 30, "rating": 9.6, "ppg": 27.8, "rpg": 12.3, "apg": 9.1},
        {"name": "Jamal Murray", "position": "G", "age": 28, "rating": 8.5, "ppg": 22.4, "rpg": 4.2, "apg": 6.8},
        {"name": "Michael Porter Jr.", "position": "F", "age": 27, "rating": 8.0, "ppg": 17.6, "rpg": 7.1, "apg": 1.9},
        {"name": "Aaron Gordon", "position": "F", "age": 30, "rating": 7.8, "ppg": 14.2, "rpg": 6.5, "apg": 3.4},
        {"name": "Christian Braun", "position": "G", "age": 24, "rating": 7.4, "ppg": 11.8, "rpg": 4.3, "apg": 2.6},
        {"name": "Russell Westbrook", "position": "G", "age": 37, "rating": 7.3, "ppg": 11.5, "rpg": 5.2, "apg": 5.8},
        {"name": "Peyton Watson", "position": "F", "age": 22, "rating": 7.0, "ppg": 8.5, "rpg": 3.8, "apg": 1.5},
        {"name": "Julian Strawther", "position": "G-F", "age": 23, "rating": 6.8, "ppg": 7.2, "rpg": 2.5, "apg": 1.2},
        {"name": "Dario Šarić", "position": "F-C", "age": 31, "rating": 6.7, "ppg": 5.8, "rpg": 3.5, "apg": 1.8},
        {"name": "Hunter Tyson", "position": "F", "age": 24, "rating": 6.5, "ppg": 4.5, "rpg": 2.1, "apg": 0.8},
        {"name": "Zeke Nnaji", "position": "F-C", "age": 24, "rating": 6.4, "ppg": 3.8, "rpg": 2.8, "apg": 0.5},
        {"name": "Jalen Pickett", "position": "G", "age": 25, "rating": 6.2, "ppg": 2.5, "rpg": 1.5, "apg": 1.8},
    ],
    "Memphis Grizzlies": [
        {"name": "Ja Morant", "position": "G", "age": 26, "rating": 9.1, "ppg": 28.9, "rpg": 5.2, "apg": 8.3},
        {"name": "Jaren Jackson Jr.", "position": "F-C", "age": 26, "rating": 8.4, "ppg": 21.5, "rpg": 6.8, "apg": 1.9},
        {"name": "Desmond Bane", "position": "G", "age": 27, "rating": 8.2, "ppg": 19.7, "rpg": 4.5, "apg": 5.1},
        {"name": "Marcus Smart", "position": "G", "age": 31, "rating": 7.6, "ppg": 11.4, "rpg": 3.8, "apg": 5.9},
        {"name": "Santi Aldama", "position": "F", "age": 26, "rating": 7.3, "ppg": 12.8, "rpg": 6.5, "apg": 2.1},
        {"name": "Scotty Pippen Jr.", "position": "G", "age": 24, "rating": 7.1, "ppg": 10.5, "rpg": 3.2, "apg": 4.8},
        {"name": "Zach Edey", "position": "C", "age": 23, "rating": 7.0, "ppg": 9.8, "rpg": 7.5, "apg": 0.8},
        {"name": "Jaylen Wells", "position": "F", "age": 22, "rating": 6.8, "ppg": 8.2, "rpg": 3.5, "apg": 1.5},
        {"name": "Luke Kennard", "position": "G", "age": 29, "rating": 6.9, "ppg": 7.5, "rpg": 2.1, "apg": 2.8},
        {"name": "Brandon Clarke", "position": "F-C", "age": 29, "rating": 6.7, "ppg": 6.8, "rpg": 4.5, "apg": 1.2},
        {"name": "Jake LaRavia", "position": "F", "age": 24, "rating": 6.5, "ppg": 5.2, "rpg": 3.1, "apg": 1.8},
        {"name": "John Konchar", "position": "G-F", "age": 29, "rating": 6.4, "ppg": 4.5, "rpg": 3.5, "apg": 2.1},
    ],
    "Detroit Pistons": [
        {"name": "Cade Cunningham", "position": "G", "age": 24, "rating": 8.9, "ppg": 26.8, "rpg": 7.2, "apg": 9.5},
        {"name": "Jaden Ivey", "position": "G", "age": 23, "rating": 8.3, "ppg": 21.4, "rpg": 4.8, "apg": 5.2},
        {"name": "Ausar Thompson", "position": "F", "age": 22, "rating": 7.9, "ppg": 14.6, "rpg": 7.1, "apg": 3.8},
        {"name": "Jalen Duren", "position": "C", "age": 21, "rating": 8.1, "ppg": 16.2, "rpg": 11.5, "apg": 2.1},
        {"name": "Tobias Harris", "position": "F", "age": 33, "rating": 7.7, "ppg": 13.8, "rpg": 6.3, "apg": 3.2},
        {"name": "Tim Hardaway Jr.", "position": "G", "age": 33, "rating": 7.2, "ppg": 12.5, "rpg": 3.1, "apg": 2.5},
        {"name": "Malik Beasley", "position": "G", "age": 28, "rating": 7.1, "ppg": 11.8, "rpg": 2.8, "apg": 1.8},
        {"name": "Simone Fontecchio", "position": "F", "age": 29, "rating": 6.9, "ppg": 9.5, "rpg": 3.5, "apg": 1.5},
        {"name": "Isaiah Stewart", "position": "F-C", "age": 24, "rating": 7.0, "ppg": 8.2, "rpg": 6.8, "apg": 1.2},
        {"name": "Ron Holland", "position": "F", "age": 20, "rating": 6.7, "ppg": 6.5, "rpg": 3.2, "apg": 1.5},
        {"name": "Marcus Sasser", "position": "G", "age": 25, "rating": 6.6, "ppg": 5.8, "rpg": 1.8, "apg": 2.5},
        {"name": "Paul Reed", "position": "C", "age": 26, "rating": 6.5, "ppg": 4.5, "rpg": 4.2, "apg": 0.8},
        {"name": "Wendell Moore Jr.", "position": "G-F", "age": 24, "rating": 6.3, "ppg": 3.2, "rpg": 2.1, "apg": 1.5},
    ],
    "Toronto Raptors": [
        {"name": "Scottie Barnes", "position": "F", "age": 24, "rating": 8.6, "ppg": 23.5, "rpg": 8.9, "apg": 6.4},
        {"name": "RJ Barrett", "position": "G-F", "age": 25, "rating": 8.2, "ppg": 21.7, "rpg": 6.2, "apg": 4.8},
        {"name": "Immanuel Quickley", "position": "G", "age": 26, "rating": 7.9, "ppg": 18.3, "rpg": 3.5, "apg": 7.1},
        {"name": "Jakob Poeltl", "position": "C", "age": 29, "rating": 7.6, "ppg": 12.4, "rpg": 9.8, "apg": 2.9},
        {"name": "Gradey Dick", "position": "G-F", "age": 21, "rating": 7.4, "ppg": 11.2, "rpg": 3.8, "apg": 2.1},
        {"name": "Ochai Agbaji", "position": "G-F", "age": 25, "rating": 7.1, "ppg": 10.5, "rpg": 3.2, "apg": 1.8},
        {"name": "Kelly Olynyk", "position": "F-C", "age": 34, "rating": 7.0, "ppg": 9.8, "rpg": 5.5, "apg": 3.2},
        {"name": "Bruce Brown", "position": "G-F", "age": 29, "rating": 6.9, "ppg": 8.5, "rpg": 4.1, "apg": 2.5},
        {"name": "Chris Boucher", "position": "F-C", "age": 32, "rating": 6.8, "ppg": 7.2, "rpg": 4.8, "apg": 0.8},
        {"name": "Davion Mitchell", "position": "G", "age": 27, "rating": 6.7, "ppg": 6.5, "rpg": 2.1, "apg": 3.5},
        {"name": "Jonathan Mogbo", "position": "F", "age": 23, "rating": 6.5, "ppg": 4.8, "rpg": 3.5, "apg": 1.5},
        {"name": "Ja'Kobe Walter", "position": "G", "age": 21, "rating": 6.4, "ppg": 3.5, "rpg": 1.8, "apg": 1.2},
    ],
    "Atlanta Hawks": [
        {"name": "Trae Young", "position": "G", "age": 27, "rating": 8.8, "ppg": 27.3, "rpg": 3.2, "apg": 11.2},
        {"name": "Dejounte Murray", "position": "G", "age": 29, "rating": 8.3, "ppg": 20.5, "rpg": 5.8, "apg": 6.9},
        {"name": "Jalen Johnson", "position": "F", "age": 23, "rating": 8.0, "ppg": 17.8, "rpg": 8.5, "apg": 4.2},
        {"name": "Clint Capela", "position": "C", "age": 31, "rating": 7.7, "ppg": 11.6, "rpg": 10.9, "apg": 1.2},
        {"name": "Bogdan Bogdanović", "position": "G", "age": 32, "rating": 7.5, "ppg": 14.2, "rpg": 3.4, "apg": 3.8},
        {"name": "De'Andre Hunter", "position": "F", "age": 27, "rating": 7.3, "ppg": 13.5, "rpg": 4.5, "apg": 1.8},
        {"name": "Dyson Daniels", "position": "G", "age": 22, "rating": 7.2, "ppg": 11.8, "rpg": 4.2, "apg": 3.5},
        {"name": "Onyeka Okongwu", "position": "C", "age": 24, "rating": 7.1, "ppg": 10.5, "rpg": 7.8, "apg": 1.5},
        {"name": "Zaccharie Risacher", "position": "F", "age": 20, "rating": 6.9, "ppg": 9.2, "rpg": 3.8, "apg": 1.5},
        {"name": "Garrison Mathews", "position": "G", "age": 28, "rating": 6.7, "ppg": 6.5, "rpg": 2.1, "apg": 1.2},
        {"name": "Vit Krejci", "position": "G", "age": 25, "rating": 6.6, "ppg": 5.8, "rpg": 2.5, "apg": 2.8},
        {"name": "Larry Nance Jr.", "position": "F-C", "age": 32, "rating": 6.8, "ppg": 5.2, "rpg": 4.5, "apg": 1.5},
    ],
    "Orlando Magic": [
        {"name": "Paolo Banchero", "position": "F", "age": 22, "rating": 8.7, "ppg": 24.8, "rpg": 7.9, "apg": 5.3},
        {"name": "Franz Wagner", "position": "F", "age": 23, "rating": 8.4, "ppg": 21.2, "rpg": 5.6, "apg": 5.8},
        {"name": "Jalen Suggs", "position": "G", "age": 24, "rating": 7.8, "ppg": 15.7, "rpg": 4.2, "apg": 4.9},
        {"name": "Wendell Carter Jr.", "position": "C", "age": 26, "rating": 7.6, "ppg": 12.8, "rpg": 9.3, "apg": 2.1},
        {"name": "Cole Anthony", "position": "G", "age": 25, "rating": 7.3, "ppg": 11.5, "rpg": 3.8, "apg": 4.2},
        {"name": "Kentavious Caldwell-Pope", "position": "G", "age": 32, "rating": 7.2, "ppg": 10.8, "rpg": 3.2, "apg": 2.5},
        {"name": "Jonathan Isaac", "position": "F", "age": 28, "rating": 7.0, "ppg": 8.5, "rpg": 5.8, "apg": 1.2},
        {"name": "Goga Bitadze", "position": "C", "age": 26, "rating": 6.9, "ppg": 7.2, "rpg": 6.5, "apg": 1.5},
        {"name": "Tristan da Silva", "position": "F", "age": 24, "rating": 6.8, "ppg": 6.8, "rpg": 3.5, "apg": 1.8},
        {"name": "Anthony Black", "position": "G", "age": 21, "rating": 6.7, "ppg": 5.5, "rpg": 2.8, "apg": 3.2},
        {"name": "Moritz Wagner", "position": "C", "age": 28, "rating": 6.6, "ppg": 5.2, "rpg": 3.8, "apg": 1.1},
        {"name": "Caleb Houstan", "position": "F", "age": 22, "rating": 6.4, "ppg": 3.8, "rpg": 2.1, "apg": 0.8},
    ],
    "Miami Heat": [
        {"name": "Jimmy Butler", "position": "F", "age": 36, "rating": 8.5, "ppg": 22.4, "rpg": 5.8, "apg": 5.2},
        {"name": "Bam Adebayo", "position": "C", "age": 28, "rating": 8.3, "ppg": 19.6, "rpg": 10.2, "apg": 4.8},
        {"name": "Tyler Herro", "position": "G", "age": 25, "rating": 8.0, "ppg": 21.8, "rpg": 4.5, "apg": 5.3},
        {"name": "Terry Rozier", "position": "G", "age": 31, "rating": 7.6, "ppg": 16.2, "rpg": 3.8, "apg": 4.9},
        {"name": "Jaime Jaquez Jr.", "position": "F", "age": 24, "rating": 7.4, "ppg": 12.5, "rpg": 5.1, "apg": 2.8},
        {"name": "Duncan Robinson", "position": "G-F", "age": 31, "rating": 7.2, "ppg": 11.8, "rpg": 2.8, "apg": 2.1},
        {"name": "Nikola Jović", "position": "F", "age": 22, "rating": 7.0, "ppg": 10.5, "rpg": 4.5, "apg": 2.5},
        {"name": "Haywood Highsmith", "position": "F", "age": 28, "rating": 6.8, "ppg": 7.2, "rpg": 3.5, "apg": 1.2},
        {"name": "Kevin Love", "position": "F-C", "age": 37, "rating": 6.9, "ppg": 6.5, "rpg": 5.8, "apg": 2.1},
        {"name": "Alec Burks", "position": "G", "age": 34, "rating": 6.7, "ppg": 5.8, "rpg": 2.1, "apg": 1.8},
        {"name": "Kel'el Ware", "position": "C", "age": 21, "rating": 6.6, "ppg": 4.5, "rpg": 3.8, "apg": 0.5},
        {"name": "Pelle Larsson", "position": "G", "age": 24, "rating": 6.4, "ppg": 3.2, "rpg": 1.5, "apg": 1.5},
    ],
    "Philadelphia 76ers": [
        {"name": "Joel Embiid", "position": "C", "age": 31, "rating": 9.3, "ppg": 29.8, "rpg": 11.5, "apg": 5.2},
        {"name": "Tyrese Maxey", "position": "G", "age": 24, "rating": 8.6, "ppg": 26.3, "rpg": 4.1, "apg": 7.8},
        {"name": "Paul George", "position": "F", "age": 35, "rating": 8.2, "ppg": 19.5, "rpg": 6.2, "apg": 4.5},
        {"name": "Kelly Oubre Jr.", "position": "F", "age": 29, "rating": 7.5, "ppg": 13.8, "rpg": 5.3, "apg": 1.9},
        {"name": "Caleb Martin", "position": "F", "age": 29, "rating": 7.3, "ppg": 10.2, "rpg": 4.8, "apg": 2.4},
        {"name": "Kyle Lowry", "position": "G", "age": 39, "rating": 7.1, "ppg": 8.5, "rpg": 3.2, "apg": 5.8},
        {"name": "Eric Gordon", "position": "G", "age": 36, "rating": 7.0, "ppg": 9.8, "rpg": 2.5, "apg": 2.1},
        {"name": "Andre Drummond", "position": "C", "age": 32, "rating": 6.9, "ppg": 7.5, "rpg": 8.8, "apg": 1.2},
        {"name": "Guerschon Yabusele", "position": "F", "age": 29, "rating": 6.8, "ppg": 6.8, "rpg": 4.2, "apg": 1.5},
        {"name": "Reggie Jackson", "position": "G", "age": 35, "rating": 6.7, "ppg": 5.5, "rpg": 1.8, "apg": 3.2},
        {"name": "KJ Martin", "position": "F", "age": 24, "rating": 6.6, "ppg": 4.8, "rpg": 3.5, "apg": 0.8},
        {"name": "Ricky Council IV", "position": "G", "age": 24, "rating": 6.4, "ppg": 3.5, "rpg": 2.1, "apg": 1.2},
    ],
    "Charlotte Hornets": [
        {"name": "LaMelo Ball", "position": "G", "age": 24, "rating": 8.7, "ppg": 25.9, "rpg": 5.8, "apg": 8.6},
        {"name": "Brandon Miller", "position": "F", "age": 22, "rating": 8.2, "ppg": 20.4, "rpg": 6.5, "apg": 3.7},
        {"name": "Miles Bridges", "position": "F", "age": 27, "rating": 7.9, "ppg": 18.7, "rpg": 7.2, "apg": 3.9},
        {"name": "Mark Williams", "position": "C", "age": 23, "rating": 7.6, "ppg": 13.5, "rpg": 10.8, "apg": 1.5},
        {"name": "Nick Richards", "position": "C", "age": 27, "rating": 7.2, "ppg": 9.8, "rpg": 7.5, "apg": 1.2},
        {"name": "Tre Mann", "position": "G", "age": 25, "rating": 7.1, "ppg": 11.5, "rpg": 3.2, "apg": 4.8},
        {"name": "Josh Green", "position": "G-F", "age": 24, "rating": 7.0, "ppg": 10.2, "rpg": 3.5, "apg": 2.5},
        {"name": "Vasilije Micić", "position": "G", "age": 31, "rating": 6.9, "ppg": 8.5, "rpg": 2.1, "apg": 4.2},
        {"name": "Cody Martin", "position": "F", "age": 30, "rating": 6.8, "ppg": 6.8, "rpg": 3.8, "apg": 2.1},
        {"name": "Grant Williams", "position": "F", "age": 26, "rating": 6.7, "ppg": 5.5, "rpg": 4.2, "apg": 1.5},
        {"name": "Tidjane Salaün", "position": "F", "age": 20, "rating": 6.5, "ppg": 4.2, "rpg": 2.8, "apg": 0.8},
        {"name": "KJ Simpson", "position": "G", "age": 24, "rating": 6.3, "ppg": 3.5, "rpg": 1.5, "apg": 2.1},
    ],
    "Chicago Bulls": [
        {"name": "Zach LaVine", "position": "G", "age": 30, "rating": 8.3, "ppg": 24.6, "rpg": 4.8, "apg": 5.2},
        {"name": "Coby White", "position": "G", "age": 25, "rating": 7.8, "ppg": 18.5, "rpg": 4.2, "apg": 5.8},
        {"name": "Nikola Vučević", "position": "C", "age": 35, "rating": 7.7, "ppg": 17.2, "rpg": 10.5, "apg": 3.4},
        {"name": "Patrick Williams", "position": "F", "age": 24, "rating": 7.4, "ppg": 12.8, "rpg": 5.9, "apg": 2.1},
        {"name": "Ayo Dosunmu", "position": "G", "age": 26, "rating": 7.3, "ppg": 11.4, "rpg": 3.5, "apg": 4.6},
        {"name": "Josh Giddey", "position": "G", "age": 23, "rating": 7.2, "ppg": 10.8, "rpg": 6.5, "apg": 6.2},
        {"name": "Lonzo Ball", "position": "G", "age": 28, "rating": 7.0, "ppg": 8.5, "rpg": 4.2, "apg": 5.5},
        {"name": "Matas Buzelis", "position": "F", "age": 21, "rating": 6.8, "ppg": 7.2, "rpg": 3.8, "apg": 1.5},
        {"name": "Jalen Smith", "position": "F-C", "age": 25, "rating": 6.7, "ppg": 6.5, "rpg": 5.2, "apg": 1.1},
        {"name": "Talen Horton-Tucker", "position": "G", "age": 24, "rating": 6.6, "ppg": 5.8, "rpg": 2.8, "apg": 2.5},
        {"name": "Julian Phillips", "position": "F", "age": 22, "rating": 6.5, "ppg": 4.5, "rpg": 3.2, "apg": 1.2},
        {"name": "Dalen Terry", "position": "G", "age": 23, "rating": 6.3, "ppg": 3.2, "rpg": 2.1, "apg": 1.8},
    ],
    "Brooklyn Nets": [
        {"name": "Mikal Bridges", "position": "F", "age": 29, "rating": 8.1, "ppg": 22.4, "rpg": 5.8, "apg": 4.2},
        {"name": "Cam Thomas", "position": "G", "age": 24, "rating": 7.9, "ppg": 21.6, "rpg": 3.5, "apg": 3.8},
        {"name": "Nic Claxton", "position": "C", "age": 26, "rating": 7.7, "ppg": 13.8, "rpg": 9.2, "apg": 2.5},
        {"name": "Cameron Johnson", "position": "F", "age": 29, "rating": 7.5, "ppg": 14.2, "rpg": 4.8, "apg": 2.9},
        {"name": "Dennis Schröder", "position": "G", "age": 32, "rating": 7.3, "ppg": 12.5, "rpg": 2.8, "apg": 6.4},
        {"name": "Dorian Finney-Smith", "position": "F", "age": 32, "rating": 7.1, "ppg": 10.8, "rpg": 5.2, "apg": 1.8},
        {"name": "Ben Simmons", "position": "G-F", "age": 29, "rating": 6.9, "ppg": 7.5, "rpg": 6.8, "apg": 5.5},
        {"name": "Day'Ron Sharpe", "position": "C", "age": 23, "rating": 6.8, "ppg": 6.2, "rpg": 5.5, "apg": 1.2},
        {"name": "Ziaire Williams", "position": "F", "age": 24, "rating": 6.7, "ppg": 5.8, "rpg": 2.8, "apg": 1.5},
        {"name": "Shake Milton", "position": "G", "age": 29, "rating": 6.6, "ppg": 4.5, "rpg": 2.1, "apg": 2.8},
        {"name": "Jalen Wilson", "position": "F", "age": 24, "rating": 6.5, "ppg": 3.8, "rpg": 2.5, "apg": 1.1},
        {"name": "Noah Clowney", "position": "F", "age": 21, "rating": 6.3, "ppg": 2.5, "rpg": 2.1, "apg": 0.5},
    ],
    "Washington Wizards": [
        {"name": "Jordan Poole", "position": "G", "age": 26, "rating": 7.8, "ppg": 21.3, "rpg": 3.5, "apg": 5.2},
        {"name": "Kyle Kuzma", "position": "F", "age": 30, "rating": 7.6, "ppg": 19.8, "rpg": 6.8, "apg": 3.9},
        {"name": "Bilal Coulibaly", "position": "F", "age": 21, "rating": 7.4, "ppg": 13.5, "rpg": 5.2, "apg": 3.1},
        {"name": "Alexandre Sarr", "position": "C", "age": 20, "rating": 7.3, "ppg": 11.8, "rpg": 8.5, "apg": 1.8},
        {"name": "Corey Kispert", "position": "F", "age": 26, "rating": 7.1, "ppg": 10.2, "rpg": 3.8, "apg": 2.4},
        {"name": "Jonas Valančiūnas", "position": "C", "age": 33, "rating": 7.2, "ppg": 12.5, "rpg": 9.8, "apg": 2.1},
        {"name": "Malcolm Brogdon", "position": "G", "age": 32, "rating": 7.0, "ppg": 11.8, "rpg": 3.2, "apg": 5.5},
        {"name": "Jared Butler", "position": "G", "age": 25, "rating": 6.8, "ppg": 8.5, "rpg": 2.1, "apg": 3.8},
        {"name": "Kyshawn George", "position": "F", "age": 21, "rating": 6.7, "ppg": 6.8, "rpg": 3.5, "apg": 1.5},
        {"name": "Bub Carrington", "position": "G", "age": 20, "rating": 6.6, "ppg": 5.2, "rpg": 2.1, "apg": 2.8},
        {"name": "Marvin Bagley III", "position": "F-C", "age": 26, "rating": 6.5, "ppg": 4.5, "rpg": 3.8, "apg": 0.8},
        {"name": "Anthony Gill", "position": "F", "age": 33, "rating": 6.3, "ppg": 3.2, "rpg": 2.5, "apg": 0.5},
    ],
    "Indiana Pacers": [
        {"name": "Tyrese Haliburton", "position": "G", "age": 25, "rating": 8.6, "ppg": 23.8, "rpg": 4.2, "apg": 11.5},
        {"name": "Pascal Siakam", "position": "F", "age": 31, "rating": 8.2, "ppg": 21.5, "rpg": 7.8, "apg": 4.2},
        {"name": "Myles Turner", "position": "C", "age": 29, "rating": 7.8, "ppg": 16.8, "rpg": 7.5, "apg": 1.5},
        {"name": "Bennedict Mathurin", "position": "G", "age": 23, "rating": 7.5, "ppg": 15.2, "rpg": 4.8, "apg": 2.9},
        {"name": "Andrew Nembhard", "position": "G", "age": 25, "rating": 7.3, "ppg": 11.5, "rpg": 3.2, "apg": 5.8},
        {"name": "Aaron Nesmith", "position": "F", "age": 26, "rating": 7.1, "ppg": 10.8, "rpg": 4.5, "apg": 1.8},
        {"name": "Obi Toppin", "position": "F", "age": 27, "rating": 7.0, "ppg": 9.5, "rpg": 5.2, "apg": 1.5},
        {"name": "T.J. McConnell", "position": "G", "age": 33, "rating": 6.9, "ppg": 7.8, "rpg": 3.1, "apg": 5.2},
        {"name": "Isaiah Jackson", "position": "C", "age": 23, "rating": 6.8, "ppg": 6.5, "rpg": 5.8, "apg": 0.8},
        {"name": "Ben Sheppard", "position": "G", "age": 24, "rating": 6.7, "ppg": 5.2, "rpg": 2.1, "apg": 1.5},
        {"name": "Jarace Walker", "position": "F", "age": 22, "rating": 6.6, "ppg": 4.5, "rpg": 3.5, "apg": 1.2},
        {"name": "Johnny Furphy", "position": "F", "age": 20, "rating": 6.4, "ppg": 2.8, "rpg": 1.8, "apg": 0.5},
    ],
    "San Antonio Spurs": [
        {"name": "Victor Wembanyama", "position": "C", "age": 21, "rating": 9.4, "ppg": 28.5, "rpg": 12.8, "apg": 4.5},
        {"name": "Devin Vassell", "position": "G", "age": 25, "rating": 8.2, "ppg": 20.8, "rpg": 4.5, "apg": 4.2},
        {"name": "Keldon Johnson", "position": "F", "age": 26, "rating": 7.8, "ppg": 17.5, "rpg": 6.2, "apg": 3.1},
        {"name": "Jeremy Sochan", "position": "F", "age": 22, "rating": 7.6, "ppg": 13.8, "rpg": 7.5, "apg": 3.8},
        {"name": "Tre Jones", "position": "G", "age": 25, "rating": 7.3, "ppg": 11.2, "rpg": 3.1, "apg": 6.9},
        {"name": "Harrison Barnes", "position": "F", "age": 33, "rating": 7.2, "ppg": 12.5, "rpg": 4.8, "apg": 2.1},
        {"name": "Stephon Castle", "position": "G", "age": 21, "rating": 7.0, "ppg": 10.8, "rpg": 3.5, "apg": 3.8},
        {"name": "Chris Paul", "position": "G", "age": 40, "rating": 7.1, "ppg": 9.5, "rpg": 3.2, "apg": 7.5},
        {"name": "Zach Collins", "position": "C", "age": 27, "rating": 6.9, "ppg": 8.2, "rpg": 5.8, "apg": 2.1},
        {"name": "Julian Champagnie", "position": "F", "age": 24, "rating": 6.8, "ppg": 7.5, "rpg": 3.2, "apg": 1.2},
        {"name": "Blake Wesley", "position": "G", "age": 23, "rating": 6.6, "ppg": 5.2, "rpg": 2.1, "apg": 2.5},
        {"name": "Sandro Mamukelashvili", "position": "F-C", "age": 26, "rating": 6.5, "ppg": 4.5, "rpg": 3.5, "apg": 1.1},
    ],
    "Los Angeles Lakers": [
        {"name": "LeBron James", "position": "F", "age": 41, "rating": 8.8, "ppg": 24.5, "rpg": 7.8, "apg": 8.2},
        {"name": "Anthony Davis", "position": "F-C", "age": 32, "rating": 9.0, "ppg": 27.3, "rpg": 11.5, "apg": 3.8},
        {"name": "Austin Reaves", "position": "G", "age": 26, "rating": 8.1, "ppg": 19.8, "rpg": 4.5, "apg": 6.2},
        {"name": "Rui Hachimura", "position": "F", "age": 27, "rating": 7.6, "ppg": 14.2, "rpg": 5.8, "apg": 2.1},
        {"name": "D'Angelo Russell", "position": "G", "age": 30, "rating": 7.5, "ppg": 15.8, "rpg": 3.2, "apg": 6.5},
        {"name": "Jarred Vanderbilt", "position": "F", "age": 26, "rating": 7.2, "ppg": 8.5, "rpg": 7.2, "apg": 1.8},
        {"name": "Gabe Vincent", "position": "G", "age": 29, "rating": 7.0, "ppg": 9.2, "rpg": 2.5, "apg": 3.5},
        {"name": "Max Christie", "position": "G", "age": 22, "rating": 6.9, "ppg": 7.8, "rpg": 2.8, "apg": 1.5},
        {"name": "Jaxson Hayes", "position": "C", "age": 25, "rating": 6.8, "ppg": 6.5, "rpg": 5.2, "apg": 0.8},
        {"name": "Cam Reddish", "position": "F", "age": 26, "rating": 6.7, "ppg": 5.8, "rpg": 2.5, "apg": 1.2},
        {"name": "Dalton Knecht", "position": "G-F", "age": 24, "rating": 6.6, "ppg": 4.5, "rpg": 2.1, "apg": 1.1},
        {"name": "Jalen Hood-Schifino", "position": "G", "age": 22, "rating": 6.4, "ppg": 3.2, "rpg": 1.5, "apg": 1.8},
    ],
    "Minnesota Timberwolves": [
        {"name": "Anthony Edwards", "position": "G", "age": 24, "rating": 9.2, "ppg": 28.7, "rpg": 5.8, "apg": 6.2},
        {"name": "Rudy Gobert", "position": "C", "age": 32, "rating": 8.2, "ppg": 13.5, "rpg": 12.8, "apg": 1.8},
        {"name": "Mike Conley", "position": "G", "age": 38, "rating": 7.7, "ppg": 11.8, "rpg": 2.9, "apg": 6.5},
        {"name": "Jaden McDaniels", "position": "F", "age": 25, "rating": 7.6, "ppg": 13.2, "rpg": 4.8, "apg": 2.4},
        {"name": "Naz Reid", "position": "C", "age": 26, "rating": 7.5, "ppg": 14.5, "rpg": 6.2, "apg": 1.9},
        {"name": "Donte DiVincenzo", "position": "G", "age": 28, "rating": 7.4, "ppg": 12.8, "rpg": 3.8, "apg": 3.5},
        {"name": "Julius Randle", "position": "F", "age": 30, "rating": 7.8, "ppg": 16.5, "rpg": 8.2, "apg": 4.1},
        {"name": "Nickeil Alexander-Walker", "position": "G", "age": 26, "rating": 7.0, "ppg": 9.5, "rpg": 2.8, "apg": 2.5},
        {"name": "Rob Dillingham", "position": "G", "age": 20, "rating": 6.8, "ppg": 7.2, "rpg": 2.1, "apg": 3.2},
        {"name": "Josh Minott", "position": "F", "age": 23, "rating": 6.6, "ppg": 5.5, "rpg": 3.5, "apg": 1.1},
        {"name": "Luka Garza", "position": "C", "age": 26, "rating": 6.5, "ppg": 4.2, "rpg": 3.2, "apg": 0.8},
        {"name": "Terrence Shannon Jr.", "position": "G", "age": 25, "rating": 6.4, "ppg": 3.5, "rpg": 1.8, "apg": 1.2},
    ],
    "Houston Rockets": [
        {"name": "Alperen Şengün", "position": "C", "age": 23, "rating": 8.6, "ppg": 23.8, "rpg": 10.5, "apg": 6.2},
        {"name": "Jalen Green", "position": "G", "age": 23, "rating": 8.3, "ppg": 24.2, "rpg": 4.8, "apg": 4.5},
        {"name": "Fred VanVleet", "position": "G", "age": 31, "rating": 7.9, "ppg": 16.5, "rpg": 3.8, "apg": 7.8},
        {"name": "Jabari Smith Jr.", "position": "F", "age": 22, "rating": 7.6, "ppg": 14.8, "rpg": 7.2, "apg": 2.1},
        {"name": "Amen Thompson", "position": "G", "age": 22, "rating": 7.4, "ppg": 12.5, "rpg": 5.8, "apg": 4.2},
        {"name": "Dillon Brooks", "position": "F", "age": 29, "rating": 7.3, "ppg": 13.8, "rpg": 4.2, "apg": 2.5},
        {"name": "Tari Eason", "position": "F", "age": 24, "rating": 7.2, "ppg": 11.5, "rpg": 6.5, "apg": 1.8},
        {"name": "Steven Adams", "position": "C", "age": 32, "rating": 7.0, "ppg": 8.5, "rpg": 8.8, "apg": 2.1},
        {"name": "Cam Whitmore", "position": "F", "age": 21, "rating": 6.9, "ppg": 9.2, "rpg": 3.5, "apg": 1.2},
        {"name": "Reed Sheppard", "position": "G", "age": 21, "rating": 6.8, "ppg": 7.5, "rpg": 2.5, "apg": 3.8},
        {"name": "Jock Landale", "position": "C", "age": 29, "rating": 6.7, "ppg": 5.8, "rpg": 4.2, "apg": 1.5},
        {"name": "Aaron Holiday", "position": "G", "age": 29, "rating": 6.5, "ppg": 4.2, "rpg": 1.8, "apg": 2.5},
    ],
    "Phoenix Suns": [
        {"name": "Kevin Durant", "position": "F", "age": 37, "rating": 8.9, "ppg": 27.8, "rpg": 6.5, "apg": 5.2},
        {"name": "Devin Booker", "position": "G", "age": 29, "rating": 8.8, "ppg": 26.5, "rpg": 4.2, "apg": 7.8},
        {"name": "Bradley Beal", "position": "G", "age": 32, "rating": 8.1, "ppg": 20.3, "rpg": 4.5, "apg": 5.1},
        {"name": "Jusuf Nurkić", "position": "C", "age": 31, "rating": 7.5, "ppg": 12.8, "rpg": 10.2, "apg": 3.5},
        {"name": "Grayson Allen", "position": "G", "age": 30, "rating": 7.3, "ppg": 11.5, "rpg": 3.2, "apg": 2.8},
        {"name": "Royce O'Neale", "position": "F", "age": 32, "rating": 7.1, "ppg": 9.8, "rpg": 4.5, "apg": 3.2},
        {"name": "Ryan Dunn", "position": "F", "age": 22, "rating": 6.9, "ppg": 8.5, "rpg": 3.8, "apg": 1.5},
        {"name": "Mason Plumlee", "position": "C", "age": 35, "rating": 6.8, "ppg": 6.2, "rpg": 6.5, "apg": 2.8},
        {"name": "Tyus Jones", "position": "G", "age": 29, "rating": 7.0, "ppg": 10.2, "rpg": 2.5, "apg": 5.5},
        {"name": "Oso Ighodaro", "position": "C", "age": 23, "rating": 6.6, "ppg": 4.5, "rpg": 3.5, "apg": 1.2},
        {"name": "Josh Okogie", "position": "G-F", "age": 26, "rating": 6.5, "ppg": 3.8, "rpg": 2.8, "apg": 1.1},
        {"name": "Bol Bol", "position": "C", "age": 25, "rating": 6.4, "ppg": 3.2, "rpg": 2.5, "apg": 0.5},
    ],
    "LA Clippers": [
        {"name": "James Harden", "position": "G", "age": 36, "rating": 8.4, "ppg": 21.5, "rpg": 5.2, "apg": 9.8},
        {"name": "Kawhi Leonard", "position": "F", "age": 34, "rating": 8.6, "ppg": 23.8, "rpg": 6.5, "apg": 4.2},
        {"name": "Norman Powell", "position": "G", "age": 32, "rating": 7.7, "ppg": 17.2, "rpg": 3.8, "apg": 2.5},
        {"name": "Ivica Zubac", "position": "C", "age": 28, "rating": 7.5, "ppg": 13.5, "rpg": 10.8, "apg": 2.1},
        {"name": "Terance Mann", "position": "G-F", "age": 29, "rating": 7.2, "ppg": 10.8, "rpg": 4.2, "apg": 3.5},
        {"name": "Derrick Jones Jr.", "position": "F", "age": 28, "rating": 7.1, "ppg": 9.5, "rpg": 4.5, "apg": 1.8},
        {"name": "Kris Dunn", "position": "G", "age": 31, "rating": 7.0, "ppg": 8.2, "rpg": 3.2, "apg": 4.5},
        {"name": "Nicolas Batum", "position": "F", "age": 37, "rating": 6.9, "ppg": 6.5, "rpg": 4.8, "apg": 2.8},
        {"name": "Bones Hyland", "position": "G", "age": 25, "rating": 6.8, "ppg": 7.8, "rpg": 2.1, "apg": 3.2},
        {"name": "Amir Coffey", "position": "G-F", "age": 28, "rating": 6.7, "ppg": 5.5, "rpg": 2.5, "apg": 1.5},
        {"name": "Kai Jones", "position": "C", "age": 24, "rating": 6.5, "ppg": 4.2, "rpg": 3.8, "apg": 0.8},
        {"name": "Jordan Miller", "position": "G-F", "age": 25, "rating": 6.3, "ppg": 3.5, "rpg": 2.1, "apg": 1.2},
    ],
    "Portland Trail Blazers": [
        {"name": "Anfernee Simons", "position": "G", "age": 26, "rating": 8.2, "ppg": 24.5, "rpg": 3.8, "apg": 6.2},
        {"name": "Shaedon Sharpe", "position": "G", "age": 22, "rating": 7.9, "ppg": 19.8, "rpg": 4.5, "apg": 3.8},
        {"name": "Jerami Grant", "position": "F", "age": 31, "rating": 7.7, "ppg": 18.2, "rpg": 5.8, "apg": 2.9},
        {"name": "Deandre Ayton", "position": "C", "age": 27, "rating": 7.8, "ppg": 16.5, "rpg": 11.2, "apg": 2.1},
        {"name": "Scoot Henderson", "position": "G", "age": 21, "rating": 7.4, "ppg": 13.8, "rpg": 3.5, "apg": 5.9},
        {"name": "Deni Avdija", "position": "F", "age": 24, "rating": 7.3, "ppg": 12.5, "rpg": 6.2, "apg": 3.5},
        {"name": "Toumani Camara", "position": "F", "age": 25, "rating": 7.0, "ppg": 9.8, "rpg": 5.5, "apg": 2.1},
        {"name": "Donovan Clingan", "position": "C", "age": 21, "rating": 6.9, "ppg": 8.5, "rpg": 7.8, "apg": 1.2},
        {"name": "Dalano Banton", "position": "G", "age": 26, "rating": 6.8, "ppg": 7.2, "rpg": 3.2, "apg": 3.8},
        {"name": "Jabari Walker", "position": "F", "age": 23, "rating": 6.7, "ppg": 5.5, "rpg": 4.2, "apg": 1.1},
        {"name": "Rayan Rupert", "position": "G-F", "age": 21, "rating": 6.5, "ppg": 4.2, "rpg": 2.5, "apg": 1.5},
        {"name": "Kris Murray", "position": "F", "age": 25, "rating": 6.4, "ppg": 3.5, "rpg": 2.1, "apg": 0.8},
    ],
    "Golden State Warriors": [
        {"name": "Stephen Curry", "position": "G", "age": 37, "rating": 8.9, "ppg": 26.8, "rpg": 4.5, "apg": 6.8},
        {"name": "Andrew Wiggins", "position": "F", "age": 30, "rating": 7.8, "ppg": 18.5, "rpg": 5.2, "apg": 3.1},
        {"name": "Jonathan Kuminga", "position": "F", "age": 23, "rating": 7.9, "ppg": 19.2, "rpg": 6.5, "apg": 3.5},
        {"name": "Draymond Green", "position": "F", "age": 35, "rating": 7.6, "ppg": 9.8, "rpg": 7.2, "apg": 6.5},
        {"name": "Brandin Podziemski", "position": "G", "age": 22, "rating": 7.3, "ppg": 12.5, "rpg": 4.8, "apg": 4.2},
        {"name": "Buddy Hield", "position": "G", "age": 32, "rating": 7.4, "ppg": 14.8, "rpg": 3.5, "apg": 2.5},
        {"name": "De'Anthony Melton", "position": "G", "age": 27, "rating": 7.1, "ppg": 10.5, "rpg": 3.8, "apg": 3.2},
        {"name": "Kevon Looney", "position": "C", "age": 29, "rating": 7.0, "ppg": 7.2, "rpg": 8.5, "apg": 2.1},
        {"name": "Kyle Anderson", "position": "F", "age": 32, "rating": 6.9, "ppg": 6.5, "rpg": 4.2, "apg": 3.5},
        {"name": "Gary Payton II", "position": "G", "age": 33, "rating": 6.8, "ppg": 5.8, "rpg": 3.2, "apg": 1.8},
        {"name": "Moses Moody", "position": "G-F", "age": 23, "rating": 6.7, "ppg": 5.2, "rpg": 2.5, "apg": 1.2},
        {"name": "Trayce Jackson-Davis", "position": "C", "age": 25, "rating": 6.6, "ppg": 4.5, "rpg": 4.8, "apg": 1.1},
    ],
    "New Orleans Pelicans": [
        {"name": "Zion Williamson", "position": "F", "age": 25, "rating": 8.7, "ppg": 26.5, "rpg": 8.2, "apg": 5.8},
        {"name": "Brandon Ingram", "position": "F", "age": 28, "rating": 8.3, "ppg": 23.8, "rpg": 5.5, "apg": 5.2},
        {"name": "CJ McCollum", "position": "G", "age": 34, "rating": 7.8, "ppg": 19.2, "rpg": 3.8, "apg": 5.5},
        {"name": "Herb Jones", "position": "F", "age": 27, "rating": 7.6, "ppg": 13.5, "rpg": 5.8, "apg": 3.2},
        {"name": "Trey Murphy III", "position": "F", "age": 25, "rating": 7.5, "ppg": 15.8, "rpg": 4.5, "apg": 2.1},
        {"name": "Dejounte Murray", "position": "G", "age": 29, "rating": 7.9, "ppg": 18.5, "rpg": 5.2, "apg": 7.2},
        {"name": "Daniel Theis", "position": "C", "age": 33, "rating": 7.0, "ppg": 8.5, "rpg": 6.8, "apg": 1.5},
        {"name": "Jose Alvarado", "position": "G", "age": 27, "rating": 6.9, "ppg": 9.2, "rpg": 2.5, "apg": 4.2},
        {"name": "Jordan Hawkins", "position": "G", "age": 23, "rating": 6.8, "ppg": 7.5, "rpg": 2.1, "apg": 1.8},
        {"name": "Yves Missi", "position": "C", "age": 21, "rating": 6.7, "ppg": 6.2, "rpg": 5.5, "apg": 0.8},
        {"name": "Javonte Green", "position": "F", "age": 32, "rating": 6.6, "ppg": 4.8, "rpg": 3.2, "apg": 1.1},
        {"name": "Antonio Reeves", "position": "G", "age": 24, "rating": 6.4, "ppg": 3.5, "rpg": 1.5, "apg": 1.2},
    ],
    "Dallas Mavericks": [
        {"name": "Luka Dončić", "position": "G", "age": 26, "rating": 9.5, "ppg": 30.5, "rpg": 8.8, "apg": 9.2},
        {"name": "Kyrie Irving", "position": "G", "age": 33, "rating": 8.6, "ppg": 24.2, "rpg": 4.5, "apg": 6.8},
        {"name": "Klay Thompson", "position": "G", "age": 35, "rating": 7.8, "ppg": 16.5, "rpg": 3.8, "apg": 2.5},
        {"name": "Daniel Gafford", "position": "C", "age": 27, "rating": 7.5, "ppg": 12.8, "rpg": 8.5, "apg": 1.5},
        {"name": "Dereck Lively II", "position": "C", "age": 21, "rating": 7.4, "ppg": 10.5, "rpg": 7.8, "apg": 1.8},
        {"name": "P.J. Washington", "position": "F", "age": 27, "rating": 7.3, "ppg": 13.2, "rpg": 6.5, "apg": 2.1},
        {"name": "Naji Marshall", "position": "F", "age": 27, "rating": 7.1, "ppg": 10.8, "rpg": 4.2, "apg": 2.8},
        {"name": "Quentin Grimes", "position": "G", "age": 25, "rating": 7.0, "ppg": 9.5, "rpg": 3.1, "apg": 2.5},
        {"name": "Maxi Kleber", "position": "F-C", "age": 33, "rating": 6.9, "ppg": 7.2, "rpg": 4.5, "apg": 1.2},
        {"name": "Jaden Hardy", "position": "G", "age": 23, "rating": 6.8, "ppg": 6.5, "rpg": 2.1, "apg": 2.1},
        {"name": "Dwight Powell", "position": "C", "age": 34, "rating": 6.7, "ppg": 4.8, "rpg": 3.8, "apg": 1.1},
        {"name": "Olivier-Maxence Prosper", "position": "F", "age": 23, "rating": 6.5, "ppg": 3.5, "rpg": 2.5, "apg": 0.8},
    ],
    "Utah Jazz": [
        {"name": "Lauri Markkanen", "position": "F", "age": 28, "rating": 8.3, "ppg": 24.5, "rpg": 8.8, "apg": 3.2},
        {"name": "Collin Sexton", "position": "G", "age": 26, "rating": 7.7, "ppg": 19.8, "rpg": 3.5, "apg": 5.2},
        {"name": "Walker Kessler", "position": "C", "age": 24, "rating": 7.6, "ppg": 13.2, "rpg": 10.5, "apg": 1.2},
        {"name": "Jordan Clarkson", "position": "G", "age": 33, "rating": 7.4, "ppg": 16.5, "rpg": 3.8, "apg": 4.5},
        {"name": "Keyonte George", "position": "G", "age": 22, "rating": 7.3, "ppg": 14.8, "rpg": 3.2, "apg": 5.8},
        {"name": "John Collins", "position": "F-C", "age": 28, "rating": 7.5, "ppg": 15.5, "rpg": 8.2, "apg": 2.1},
        {"name": "Cody Williams", "position": "F", "age": 21, "rating": 6.9, "ppg": 8.5, "rpg": 3.5, "apg": 2.1},
        {"name": "Brice Sensabaugh", "position": "F", "age": 22, "rating": 6.8, "ppg": 7.2, "rpg": 2.8, "apg": 1.2},
        {"name": "Taylor Hendricks", "position": "F", "age": 22, "rating": 6.7, "ppg": 6.5, "rpg": 4.2, "apg": 1.1},
        {"name": "Isaiah Collier", "position": "G", "age": 21, "rating": 6.6, "ppg": 5.8, "rpg": 2.1, "apg": 3.5},
        {"name": "Drew Eubanks", "position": "C", "age": 28, "rating": 6.5, "ppg": 4.5, "rpg": 4.8, "apg": 0.8},
        {"name": "Kyle Filipowski", "position": "C", "age": 22, "rating": 6.4, "ppg": 3.2, "rpg": 3.5, "apg": 1.1},
    ],
    "Sacramento Kings": [
        {"name": "De'Aaron Fox", "position": "G", "age": 27, "rating": 8.6, "ppg": 26.8, "rpg": 4.5, "apg": 7.2},
        {"name": "Domantas Sabonis", "position": "C", "age": 29, "rating": 8.4, "ppg": 20.5, "rpg": 12.8, "apg": 7.5},
        {"name": "DeMar DeRozan", "position": "F", "age": 36, "rating": 7.9, "ppg": 19.2, "rpg": 4.8, "apg": 5.2},
        {"name": "Keegan Murray", "position": "F", "age": 24, "rating": 7.5, "ppg": 15.8, "rpg": 6.2, "apg": 2.1},
        {"name": "Kevin Huerter", "position": "G", "age": 27, "rating": 7.3, "ppg": 12.5, "rpg": 3.5, "apg": 3.8},
        {"name": "Malik Monk", "position": "G", "age": 27, "rating": 7.4, "ppg": 14.2, "rpg": 3.2, "apg": 5.5},
        {"name": "Trey Lyles", "position": "F", "age": 30, "rating": 7.0, "ppg": 9.5, "rpg": 5.2, "apg": 1.8},
        {"name": "Keon Ellis", "position": "G", "age": 25, "rating": 6.9, "ppg": 7.8, "rpg": 2.8, "apg": 2.5},
        {"name": "Alex Len", "position": "C", "age": 32, "rating": 6.8, "ppg": 6.5, "rpg": 5.8, "apg": 1.2},
        {"name": "Devin Carter", "position": "G", "age": 23, "rating": 6.7, "ppg": 5.2, "rpg": 2.1, "apg": 2.8},
        {"name": "Jordan McLaughlin", "position": "G", "age": 29, "rating": 6.6, "ppg": 4.5, "rpg": 1.8, "apg": 3.2},
        {"name": "Isaac Jones", "position": "F", "age": 25, "rating": 6.4, "ppg": 3.2, "rpg": 2.5, "apg": 0.8},
    ]
}

def get_team_players(league, team_name):
    """팀의 선수 목록 반환"""
    # 한국 리그는 별도 로스터 파일 사용
    if league == 'KBO':
        try:
            from data.kbo_rosters_complete_2026 import KBO_ROSTERS_2026
            import copy
            # 깊은 복사로 원본 데이터 보호
            return copy.deepcopy(KBO_ROSTERS_2026.get(team_name, []))
        except ImportError as e:
            print(f"KBO 로스터 import 실패: {e}")
            pass
    elif league == 'K리그1':
        try:
            from data.kleague_rosters_complete_2026 import KLEAGUE_ROSTERS_2026
            import copy
            # 깊은 복사로 원본 데이터 보호
            return copy.deepcopy(KLEAGUE_ROSTERS_2026.get(team_name, []))
        except ImportError as e:
            print(f"K리그1 로스터 import 실패: {e}")
            pass
    elif league == 'KBL':
        try:
            from data.kbl_rosters_complete_2025_26 import KBL_ROSTERS_2025_26
            import copy
            # 깊은 복사로 원본 데이터 보호
            return copy.deepcopy(KBL_ROSTERS_2025_26.get(team_name, []))
        except ImportError as e:
            print(f"KBL 로스터 import 실패: {e}")
            pass
    elif league == 'V-리그 남자':
        try:
            from data.vleague_rosters_complete_2025_26 import VLEAGUE_MEN_ROSTERS_2025_26
            import copy
            # 깊은 복사로 원본 데이터 보호
            return copy.deepcopy(VLEAGUE_MEN_ROSTERS_2025_26.get(team_name, []))
        except ImportError as e:
            print(f"V-리그 남자 로스터 import 실패: {e}")
            pass
    elif league == 'V-리그 여자':
        try:
            from data.vleague_rosters_complete_2025_26 import VLEAGUE_WOMEN_ROSTERS_2025_26
            import copy
            # 깊은 복사로 원본 데이터 보호
            return copy.deepcopy(VLEAGUE_WOMEN_ROSTERS_2025_26.get(team_name, []))
        except ImportError as e:
            print(f"V-리그 여자 로스터 import 실패: {e}")
            pass
    
    # 기존 리그 데이터
    players_data = {
        "La Liga": LA_LIGA_PLAYERS,
        "Bundesliga": BUNDESLIGA_PLAYERS,
        "Serie A": SERIE_A_PLAYERS,
        "EPL": EPL_PLAYERS,
        "NBA East": NBA_PLAYERS,
        "NBA West": NBA_PLAYERS,
    }
    
    league_players = players_data.get(league, {})
    return league_players.get(team_name, [])

def get_player_stats(league, team_name, player_name):
    """특정 선수 통계 반환"""
    players = get_team_players(league, team_name)
    for player in players:
        if player['name'] == player_name:
            return player
    return None

def get_all_players_count():
    """전체 선수 수 반환"""
    total = 0
    for league_players in [LA_LIGA_PLAYERS, BUNDESLIGA_PLAYERS, SERIE_A_PLAYERS, EPL_PLAYERS, NBA_PLAYERS]:
        for team_players in league_players.values():
            total += len(team_players)
    return total
