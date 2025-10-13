# Broke.io

A modern, web-based reimagination of Monopoly! Build your empire, trade properties, and bankrupt rivals in this fast-paced strategy game featuring animated boards, timed auctions, power-ups, and live chat.

## 🎮 Features

- **🎲 Animated Game Board**: Beautiful, interactive Monopoly-style board with smooth animations
- **⏱️ Timed Auctions**: Competitive property auctions with countdown timers
- **⚡ Power-ups**: Special abilities to gain advantages:
  - Double Dice: Roll with advantage
  - Rent Shield: Protection from rent payments
  - Property Swap: Force property trades
  - Banker's Boost: Get bonus money
- **💬 Live Chat**: Real-time communication with other players
- **🎮 Mini-games**: Random challenges to earn extra cash:
  - Target Click
  - Memory Match
  - Quick Math
- **📊 Player Progression**: Level up system with experience points
- **🏆 Leaderboards**: Compete with players worldwide
- **🎨 Themed Worlds**: Multiple board themes:
  - Classic
  - Cyber City
  - Fantasy Realm
  - Space Station
- **👥 Multiple Game Modes**:
  - Solo (play against AI)
  - Friends (local multiplayer)
  - Online (play with others globally)
- **🎭 Customizable Tokens**: Choose from 8 different player tokens

## 🚀 Getting Started

### Prerequisites

No installation required! Just a modern web browser (Chrome, Firefox, Safari, or Edge).

### How to Play

1. **Open the Game**
   ```bash
   # Simply open index.html in your web browser
   open index.html
   ```
   Or drag and drop `index.html` into your browser.

2. **Choose Your Game Mode**
   - Click **Solo** to play against AI bots
   - Click **Friends** for local multiplayer
   - Click **Online** to play with others (coming soon)

3. **Customize Your Token**
   - Click on your player token to choose from 8 different options

4. **Start Playing**
   - Click **Roll Dice** to move around the board
   - Buy properties when you land on them
   - Pay rent when landing on opponent properties
   - Use power-ups strategically to gain advantages

5. **Win the Game**
   - Bankrupt your opponents by owning properties and collecting rent
   - Build monopolies to charge higher rent
   - Use mini-games and power-ups to maximize your wealth

## 🎯 Game Rules

### Basic Gameplay
- Start with $1,500
- Roll dice to move around the board
- Collect $200 when passing GO
- Buy unowned properties you land on
- Pay rent when landing on owned properties

### Properties
- Each property has a purchase price and rent value
- Own all properties of the same color to form a monopoly
- Build houses and hotels to increase rent (coming soon)

### Special Spaces
- **GO**: Collect $200
- **Income Tax**: Pay $200
- **Luxury Tax**: Pay $100
- **Jail**: Just visiting or in jail
- **Free Parking**: Safe space
- **Community Chest**: Special cards (coming soon)
- **Chance**: Special cards (coming soon)

### Power-ups
Purchase power-ups during your turn:
- **Double Dice** ($100): Roll with advantage next turn
- **Rent Shield** ($150): Protected from rent for 3 turns
- **Property Swap** ($200): Force a property trade
- **Banker's Boost** ($250): Receive $500 bonus

### Mini-games
Randomly triggered during gameplay:
- Complete challenges within 30 seconds
- Earn bonus money based on your score
- Gain experience points for leveling up

## 🎨 Themes

Change the board theme from the side panel:
- **Classic**: Traditional Monopoly look
- **Cyber City**: Futuristic neon aesthetic
- **Fantasy Realm**: Magical purple theme
- **Space Station**: Dark space theme

## 📁 Project Structure

```
Broke.io/
├── index.html          # Main game page
├── css/
│   └── style.css      # Game styles and animations
├── js/
│   ├── game.js        # Core game logic
│   ├── board.js       # Board animations
│   ├── auction.js     # Auction system
│   ├── chat.js        # Chat functionality
│   ├── powerups.js    # Power-up system
│   └── minigames.js   # Mini-games
└── README.md          # This file
```

## 🔧 Development

### File Structure
- **HTML**: Single-page application in `index.html`
- **CSS**: All styles in `css/style.css` with animations and responsive design
- **JavaScript**: Modular JS files for different game features

### Adding New Features
- **New Properties**: Edit the `propertyData` array in `js/game.js`
- **New Power-ups**: Add to `powerupDefinitions` in `js/powerups.js`
- **New Mini-games**: Add to `minigames` object in `js/minigames.js`
- **New Themes**: Add theme styles in `css/style.css`

## 🎮 Controls

- **Mouse**: Click to interact with all game elements
- **Roll Dice**: Click the "Roll Dice" button in the center
- **Buy Property**: Click property spaces or use the buy button in the modal
- **Use Power-ups**: Click power-up buttons in the side panel
- **Chat**: Type messages and press Enter or click Send
- **Theme Change**: Use the dropdown in the side panel

## 🌟 Tips for Success

1. **Buy properties early** to start collecting rent
2. **Form monopolies** (own all properties of one color) for maximum rent
3. **Use power-ups strategically** at critical moments
4. **Complete mini-games** for bonus income
5. **Trade properties** with other players to build monopolies
6. **Manage your money** - don't go bankrupt!

## 🚧 Coming Soon

- Online multiplayer with WebSocket
- Trading system between players
- Building houses and hotels
- Community Chest and Chance cards
- Mobile app version
- More mini-games
- Tournament mode
- Achievements and badges
- Save/load game state

## 📄 License

This project is open source and available for educational purposes.

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest new features
- Submit pull requests
- Improve documentation

## 👨‍💻 Author

Created with ❤️ for the digital age of capitalism!

---

**Enjoy playing Broke.io!** 🎲💰🏆
