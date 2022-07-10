# AbsurdlyWholesome
An AI made to automatically take the Turing Test on Reddit, based on [this](https://github.com/yashar1/reddit-comment-bot) original project by [yashar1](https://github.com/yashar1).

## Results
https://drive.google.com/file/d/13HiMi7CGQpbo_nHiCAC4-8-0JSjvrhad/view?usp=sharing

## Notes and Lessons
1. I have difficulties making the bot work in subreddits about art, as the bot will claim the art to be theirs, every time.
2. The bot is better at questions, and often deliver very precise answers.
3. The bot tends to simply agree with the posted comment, and therefore enhancing the eccochamber effect, which is not the wanted result. But the openai values could be better adjust (possibly based on feedback comments received)
4. The bot has a hard time understanding the concept of talking about a third character. When a comment, is a commentary on the post, the bot thinks that the comment is related to the bot.
The bot doesn't always do a good job of reading the room: "Himmler was a cowardly little worm, but he was also a genius. He was able to rise to the top of the Nazi party and lead it to victory in World War II." - AbsurdlyWholesome, in a post about a picture of Himmler having a staring contest with a concentration camp worker.

## Ideas
An index to show the value of a comment, as so the AI can distinguish between comment worth an answer, and "spam"-like comments
