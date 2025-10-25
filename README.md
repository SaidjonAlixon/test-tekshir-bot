# Test Tekshir Bot

Telegram bot for creating and taking tests with advanced features.

## Features

- ✅ Create tests with custom questions and answers
- ✅ Take tests using unique test codes
- ✅ Real-time result calculation and display
- ✅ Admin panel for comprehensive test management
- ✅ Excel export functionality for results
- ✅ Subscription check for channel members
- ✅ Secure database operations with context managers
- ✅ Error handling and user-friendly messages
- ✅ Multi-language support (Uzbek)

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Abdujabbor0720/Uyg-un-learning-platform.git
   cd test-tekshir-bot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env file with your values
   ```

4. **Run the bot**
   ```bash
   python bot.py
   ```

## Environment Variables

Create a `.env` file with the following variables:

```env
# Bot token from @BotFather
BOT_TOKEN=your_bot_token_here

# Admin user IDs (comma separated)
ADMIN_IDS=123456789,987654321

# Channel for subscription check
OPEN_CHANNEL=@your_channel_username

# Closed group for results
CLOSED_GROUP_ID=-1001234567890
```

## Usage

### For Admins
1. Start the bot with `/start` command
2. Use "➕ Test yaratish" to create new tests
3. Set test name, question count, and correct answers
4. Share the generated test code with users
5. View results and export to Excel

### For Users
1. Subscribe to the required channel
2. Use "🧪 Test ishlash" to take tests
3. Enter the test code provided by admin
4. Submit your answers in the specified format
5. View your results immediately

## Database Schema

The bot uses SQLite database with the following tables:
- `tests`: Stores test information
- `results`: Stores user test results
- `admins`: Stores admin user IDs
- `settings`: Stores bot settings

## API Features

- **Test Creation**: Admins can create tests with custom questions
- **Test Taking**: Users can take tests using unique codes
- **Result Calculation**: Automatic scoring and percentage calculation
- **Excel Export**: Download results in Excel format
- **Subscription Check**: Verify channel membership before access

## Error Handling

The bot includes comprehensive error handling:
- Database connection errors
- Invalid test codes
- Subscription verification failures
- File upload/download errors

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support and questions, contact: @NChBadmin0309

## Author

Created by: @Tolov_admini_btu
