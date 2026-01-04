// 🍛 Local Recipe Database
const recipes = [];
const shoppingList = [];
const USER_HEALTH_KEY = "userHealthConditions";
const getApiBaseUrl = () => window.API_BASE_URL || deriveApiBase();

function deriveApiBase() {
  if (window.location.port && window.location.port !== '3000') {
    return `${window.location.origin}/api`;
  }
  return `${window.location.protocol}//${window.location.hostname}:8005/api`;
}

// ------------- Gemini Bridge -----------------
async function askGemini(text) {
  try {
    const token = localStorage.getItem('accessToken');
    if (!token) {
      return "Please log in to chat with VitaBot.";
    }

    const res = await fetch(`${getApiBaseUrl()}/gemini`, {
      method: "POST",
      headers: { 
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`
      },
      body: JSON.stringify({ message: text })
    });
    
    if (!res.ok) {
      throw new Error('Gemini request failed');
    }

    const data = await res.json();
    return (data.reply || "🤖 VitaBot didn't respond.").replace(/\*\*/g, "").replace(/\*/g, "");
  } catch (err) {
    console.error("Gemini fetch error:", err);
    return "⚠️ Couldn't reach VitaBot right now. I'm here to help with health tips, recipes, and wellness advice!";
  }
}

// 🍽️ Fetch from Spoonacular if local search fails
async function fetchRecipesFromAPI(ingredients) {
  try {
    const token = localStorage.getItem('accessToken');
    if (!token) {
      return "Please log in to fetch personalized recipes.";
    }

    const params = new URLSearchParams({ ingredients, limit: 3 });
    const response = await fetch(`${getApiBaseUrl()}/recipes/search?${params.toString()}`, {
      headers: {
        "Authorization": `Bearer ${token}`
      }
    });

    if (!response.ok) throw new Error("Recipe API response was not ok");
    const data = await response.json();

    if (!data || data.length === 0) return "Hmm, no recipes found 😢. Try different ingredients.";

    return "Here are some ideas!💡 \n\n" +
      data.map(recipe => `• ${recipe.title}`).join("\n");
  } catch (error) {
    console.error("Fetch error:", error);
    return "Oops! Couldn’t fetch recipes right now. Please try again later.";
  }
}

// ------------- Chat UI Helpers --------------
function addMessage(sender, text) {
  const chatbox = document.getElementById("chatbox");
  const div = document.createElement("div");
  div.className = sender === "user" ? "user-message" : "bot-message";
  div.textContent = ""; // we'll type it out
  chatbox.appendChild(div);
  typeReply(div, text);
  chatbox.scrollTop = chatbox.scrollHeight;
  chatHistory.push({ sender, text }); 
}

function typeReply(el, text) {
  let i = 0;
  const timer = setInterval(() => {
    if (i < text.length) {
      el.textContent += text.charAt(i);
      i++;
    } else clearInterval(timer);
  }, 20);
}

// 📝 Chat form submit handler
document.getElementById("chat-form").addEventListener("submit", async function (e) {
  e.preventDefault();

  const userInput = document.getElementById("user-input");
  const message = userInput.value.trim();

  if (message === "") return;

  addMessage("user", message);
  userInput.value = "";
  userInput.disabled = true; // Disable input while processing


  // Handle async reply logic
  const botReply = await getBotReply(message);
  addMessage("bot", botReply);
  userInput.disabled = false; // Re-enable input
});

// Chat history array
let chatHistory = [];

// 🧠 Bot reply logic
async function getBotReply(input) {
  const message = input.toLowerCase();

  const containsAny = (keywords) => keywords.some(k => message.includes(k));

  if (message === "debug reminders") {
    return `🧪 Reminder ON: ${localStorage.getItem("dailyReminderOptIn")}, Natural Tips ON: ${localStorage.getItem("dailyNaturalTips")}`;
  }

  if (["hello", "hi", "namaste", "hey", "good morning"].some(greet => message.includes(greet))) {
    return "Namaste! I'm VitaBot 🌿 How can I assist you on your wellness journey today?";
  }

  if (containsAny(["thank you", "thanks", "thx"])){
    return "😊 You're welcome! I'm always here for you. 💚";
  }
  if (containsAny(["goodbye", "bye"])){
    return "👋 Bye for now! Stay healthy and hydrated! 💧";
  }

  // 🧘‍♀️1. Exercise Recommender
  const exerciseKeywords = [
    "exercise", "workout", "stretch", "move", "i feel stiff",
    "pcod", "anxiety workout", "backpain", "neckpain", "lowenergy",
    "focus", "anger", "headache", "morning", "evening", "quick fitness",
    "cardio", "strength", "yoga", "pilates", "running", "walking",
    "gym", "home workout", "beginner", "advanced", "weight loss exercise"
  ];
  if (containsAny(exerciseKeywords)) {
    const conditionBasedWorkouts = {
      pcod: "🧘‍♀️ For PCOD: Try 3 rounds of Surya Namaskar, light walking, and pelvic tilts. Avoid heavy cardio.",
      stress: "🧘‍♂️ Feeling stressed? Try this: 1 min deep breathing + 10 slow neck rolls + 5 min walk outside.",
      depression: "💪 Feeling low? Try this energizer: 20 jumping jacks, 10 bodyweight squats, 30 sec dance break!",
      tired: "😴 Try 3 min stretch: shoulder rolls, toe touches, side stretches, and 5 deep breaths.",
      anxiety: "🌬️ Anxious? Try 2 min of box breathing, wall push-ups x10, and a slow walk around your room.",
      backpain: "🪑 Sitting too long? Do 10 cat-cow stretches, 5 seated spinal twists, and 1 min bridge hold.",
      neckpain: "🧖‍♀️ Neck tension? Try 5 head tilts each side, 10 chin tucks, and slow shoulder circles.",
      lowenergy: "⚡ Boost energy: 10 high knees, 10 jumping jacks, and 5 deep breaths with arm stretches.",
      focus: "🎯 Can't focus? Try 10 squats, 1 min mindful breathing, and 10 alternating arm swings.",
      anger: "🔥 Feeling angry? Shake it out with 15 jumping jacks, 10 fast punches (air), and 2 min calming breath.",
      headache: "🧊 Headache? Try 1 min temple massage, 30 sec forward fold, and gentle eye palming.",
      morning: "🌞 Morning boost: 10 sun breaths, 10 lunges, and a 30-sec stretch toward the sky.",
      evening: "🌙 Wind down: 1 min forward fold, 5 seated twists, and 3 min legs-up-the-wall pose.",
      cardio: "🏃‍♀️ Cardio time! Try: 5 min warm-up walk, 10 min jogging in place, 5 min cool-down. Great for heart health!",
      strength: "💪 Strength training: 10 push-ups, 15 squats, 10 lunges each leg, 30 sec plank. Repeat 2-3 times!",
      yoga: "🧘‍♀️ Yoga flow: Start with 5 sun salutations, then try downward dog, warrior poses, and finish with savasana.",
      beginner: "🌱 Beginner-friendly: Start with 10 min walking, 5 min stretching, and 5 min light bodyweight exercises.",
      "weight loss": "⚖️ Weight loss workout: 20 min cardio (walking/jogging), 10 min strength (squats, lunges), 5 min stretching.",
      default: "💪 Here's a quick 5-min refresh: 10 jumping jacks, 10 squats, 20 arm circles, and 5 deep breaths!"
    };

    const lowerMsg = message.toLowerCase();
    const matchedKey = Object.keys(conditionBasedWorkouts).find(key => lowerMsg.includes(key));

    const userConditions = JSON.parse(localStorage.getItem(USER_HEALTH_KEY)) || [];
    const fallbackCondition = userConditions.find(c => conditionBasedWorkouts[c]);

    const response = matchedKey
      ? conditionBasedWorkouts[matchedKey]
      : (fallbackCondition ? conditionBasedWorkouts[fallbackCondition] : conditionBasedWorkouts["default"]);

    return `Ready to move? 🙆‍♀️ Here's something for you:\n\n${response}`;
  }

  // 🔍2. Health Conditions & Practical Tips
  const knownConditions = {
    diabetes: `🍬 For diabetes: Monitor carbs, avoid sugary snacks, and do regular walks or yoga.
🥗 Food Tip: Include whole grains, legumes, and cinnamon in your diet. Avoid white rice and sugary drinks.
💡 Mood Tip: Try a fun walk with music or light stretching in the sunlight!`,

    stress: `😣 Feeling stressed? Deep breathing, meditation, or a short walk in nature can really help.
🥗 Food Tip: Try magnesium-rich foods like spinach, dark chocolate, or almonds.
💡 Mood Tip: Watch a comedy or journal your thoughts!`,

    bp: `💓 Managing BP? Limit salt, stay active, and do light yoga or breathing exercises.
🥗 Food Tip: Eat potassium-rich foods like bananas, sweet potatoes, and beetroot. Avoid packaged salty snacks.
💡 Mood Tip: Listening to peaceful music or practicing gratitude helps.`,

    hypertension: `🧘 Try slow walks, low-sodium diets, and breathing exercises to manage hypertension.
🥗 Food Tip: Add garlic, oats, and leafy greens to your meals. Avoid red meat and excess caffeine.
💡 Mood Tip: Light reading or a phone call with loved ones helps relax.`,

    anxiety: `🌬️ Deep breaths! Meditation, journaling, and soft music can calm your anxiety.
🥗 Food Tip: Include omega-3 rich foods like walnuts or flaxseeds. Avoid caffeine and sugar spikes.
💡 Mood Tip: Try doodling or calling a close friend.`,

    insomnia: `😴 Can't sleep? Avoid screens before bed, dim the lights, try warm tea or calm music.
🥗 Food Tip: Try a banana or warm milk before bed. Avoid caffeine after 5 PM.
💡 Mood Tip: Read a short story or listen to rain sounds.`,

    pcod: `🌼 For PCOD, try light cardio, yoga (Surya Namaskar), and reduce sugar and junk.
🥗 Food Tip: Go for high-fiber foods, spearmint tea, and avoid dairy if it triggers symptoms.
💡 Mood Tip: Dancing or chatting with a friend can uplift your mood!`,

    depression: `💭 For depression, regular light exercise, daylight exposure, and routine can help.
🥗 Food Tip: Eat foods rich in vitamin D (eggs, mushrooms) and folate (lentils, broccoli). Avoid processed junk.
💡 Mood Tip: Try upbeat music, doodling, or small creative tasks.`,

    thyroid: `🦋 For thyroid issues, get regular checkups and stay active with light exercises.
🥗 Food Tip: Include iodine-rich foods like seaweed and eggs, and selenium-rich foods like Brazil nuts. Avoid soy-based and processed foods if they trigger symptoms.
💡 Mood Tip: Gentle yoga or journaling can help manage stress levels.`,

    obesity: `⚖️ Managing obesity? Focus on portion control, regular movement, and hydration.
🥗 Food Tip: Eat fiber-rich foods like oats, lentils, fruits, and vegetables. Avoid sugary and fried foods.
💡 Mood Tip: Set small goals and reward yourself with non-food treats like music or art time.`,

    anemia: `🩸 For anemia, ensure iron intake and avoid drinking tea/coffee with iron-rich meals.
🥗 Food Tip: Eat spinach, beetroot, pomegranates, and lentils. Pair with vitamin C foods like oranges to boost iron absorption.
💡 Mood Tip: Try reading under sunlight or light stretching to reduce fatigue.`,

    acne: `🌿 Battling acne? Maintain a skincare routine and reduce oily food intake.
🥗 Food Tip: Drink more water, and eat foods rich in zinc and vitamin A like carrots, pumpkin seeds, and yogurt. Avoid dairy if it causes flare-ups.
💡 Mood Tip: Listen to calming music and stay confident—your skin doesn’t define you!`,

    sinusitis: `🤧 For sinusitis, keep your environment clean and try steam inhalation regularly.
🥗 Food Tip: Eat spicy foods like pepper, ginger, and garlic to clear sinuses. Stay away from dairy if it worsens symptoms.
💡 Mood Tip: Do deep breathing exercises or spend time in fresh air to feel relaxed.`
  };

  // Check if any known condition is mentioned
  const mentionedConditions = Object.keys(knownConditions).filter(cond =>
    message.includes(cond)
  );

  if (mentionedConditions.length > 0 && !message.includes("workout") && !message.includes("recipe")) {
    localStorage.setItem(USER_HEALTH_KEY, JSON.stringify(mentionedConditions));
    return mentionedConditions.map(cond => `🔹 ${knownConditions[cond]}`).join("\n\n");
  }

  // 🍱 3. Recipe Suggestor (YOUR snippet integrated)
  if (message.includes("ingredients") || message.includes("recipe") || message.includes("suggest")) {
    // If condition + recipe keyword, return the specific recipe
    if (mentionedConditions.length > 0) {
      const healthConditionRecipes = {
        diabetes: `🍽️ Diabetes-Friendly Recipe: Cinnamon Lentil Porridge

Ingredients:
- 1/2 cup lentils
- 1 cup water
- 1/2 tsp cinnamon powder
- 1 tsp honey (optional)
- A pinch of salt

Instructions:
1. Rinse lentils and boil in water until soft (about 15 mins).
2. Add cinnamon and a pinch of salt; cook for another 2 minutes.
3. Drizzle honey if desired.
4. Serve warm for a healthy start!`,

        stress: `🍽️ Stress Relief Smoothie

Ingredients:
- 1 cup fresh spinach leaves
- 1 tbsp dark chocolate chips
- 10 almonds
- 1 cup almond milk or regular milk
- 1 banana

Instructions:
1. Blend all ingredients until smooth.
2. Pour into a glass and enjoy a calming, nutritious smoothie!`,

        anxiety: `🍽️ Calming Omega-3 Salad

Ingredients:
- 1 cup mixed greens
- 2 tbsp walnuts
- 1 tbsp flaxseeds
- 1/2 avocado, sliced
- 1 tbsp olive oil and lemon dressing

Instructions:
1. Toss greens, walnuts, flaxseeds, and avocado in a bowl.
2. Drizzle with olive oil and lemon juice dressing.
3. Enjoy this omega-3 rich salad to soothe anxiety.`,

        insomnia: `🍽️ Sleep-Friendly Banana Nut Oatmeal

Ingredients:
- 1/2 cup oats
- 1 cup milk or almond milk
- 1 ripe banana, mashed
- 1 tbsp chopped walnuts
- 1 tsp honey (optional)

Instructions:
1. Cook oats in milk until soft.
2. Stir in mashed banana and walnuts.
3. Drizzle honey if desired.
4. Eat warm about an hour before bedtime.`,

        pcod: `🍽️ PCOD Friendly High-Fiber Salad

Ingredients:
- 1 cup mixed leafy greens
- 1/2 cup chickpeas (boiled)
- 1/4 cup chopped cucumber
- 1/4 cup diced tomatoes
- 1 tbsp olive oil and lemon dressing

Instructions:
1. Mix all ingredients in a bowl.
2. Toss with olive oil and lemon juice.
3. Enjoy a fiber-rich meal that supports PCOD management.`,

        depression: `🍽️ Mood-Boosting Lentil Soup

Ingredients:
- 1 cup lentils
- 1 small onion, chopped
- 1 carrot, diced
- 2 cups vegetable broth
- 1 tsp turmeric
- Salt and pepper to taste

Instructions:
1. Sauté onion and carrot until soft.
2. Add lentils, broth, turmeric, salt, and pepper.
3. Simmer until lentils are cooked (about 20 mins).
4. Serve warm to help uplift mood.`,

        thyroid: `🍽️ Thyroid Support Seaweed Salad

Ingredients:
- 1/2 cup soaked seaweed (wakame or similar)
- 1/4 cup sliced cucumber
- 1 tsp sesame seeds
- 1 tbsp rice vinegar
- 1 tsp soy sauce (optional)

Instructions:
1. Mix soaked seaweed and cucumber in a bowl.
2. Toss with rice vinegar and soy sauce.
3. Sprinkle sesame seeds on top.
4. Enjoy this iodine-rich salad to support thyroid health.`,

        obesity: `🍽️ Low-Calorie Veggie Stir-Fry

Ingredients:
- 1 cup broccoli florets
- 1/2 cup sliced bell peppers
- 1/2 cup snap peas
- 1 clove garlic, minced
- 1 tbsp olive oil
- Soy sauce to taste

Instructions:
1. Heat olive oil in a pan and sauté garlic.
2. Add vegetables and stir-fry until tender-crisp.
3. Add soy sauce and cook for 1 more minute.
4. Serve hot as a nutritious low-calorie meal.`,

        anemia: `🍽️ Iron-Rich Beetroot Salad

Ingredients:
- 1 cup grated beetroot
- 1/2 cup chopped spinach
- 1/4 cup pomegranate seeds
- 1 tbsp lemon juice
- Salt and pepper to taste

Instructions:
1. Combine beetroot, spinach, and pomegranate seeds in a bowl.
2. Toss with lemon juice, salt, and pepper.
3. Enjoy a fresh salad rich in iron and vitamin C.`,

        acne: `🍽️ Skin-Friendly Carrot & Pumpkin Seed Snack

Ingredients:
- 1 cup carrot sticks
- 2 tbsp pumpkin seeds
- 1 tbsp hummus (optional)

Instructions:
1. Snack on fresh carrot sticks with pumpkin seeds.
2. Dip in hummus if desired.
3. This combo provides vitamin A and zinc to support healthy skin.`,

        sinusitis: `🍽️ Spicy Ginger Garlic Soup

Ingredients:
- 2 cups vegetable broth
- 1-inch ginger, sliced
- 2 cloves garlic, minced
- 1/4 tsp black pepper
- 1 tsp chili flakes (optional)

Instructions:
1. Boil broth with ginger and garlic for 10 minutes.
2. Add black pepper and chili flakes.
    3. Strain and sip warm to relieve sinus congestion.`,

        bp: `🍽️ Blood Pressure Friendly Roasted Veggies

Ingredients:
- 1 medium sweet potato, diced
- 1 small beetroot, diced
- 1 banana (for a smoothie or snack)
- Olive oil, salt (limited), and pepper

Instructions:
1. Toss sweet potato and beetroot with olive oil, salt, and pepper.
2. Roast in oven at 200°C (400°F) for 25-30 minutes.
3. Serve warm as a side dish, and enjoy banana as a fresh snack.`
      };

      return mentionedConditions.map(cond => healthConditionRecipes[cond] || "").join("\n\n");
    }

    // Your recipe list and fetch fallback integration
    const ingredientsList = message.match(/\b\w+\b/g) || [];
    const matchedRecipes = recipes.filter(recipe =>
      recipe.ingredients.every(ing => ingredientsList.includes(ing))
    );

    if (matchedRecipes.length > 0) {
      return matchedRecipes.map(r => `• ${r.name}: ${r.response}`).join("\n\n");
    } else {
      return await fetchRecipesFromAPI(ingredientsList.join(","));
    }
  }

  // 🥗 4. Diet Coach - Meal feedback
  if (message.includes("i had") || message.includes("ate") || message.includes("meal")) {
    const responses = [
      "Yum! 🍽️ That sounds tasty! Next time, try adding some veggies for a fiber boost.",
      "Ooh, delicious choice! 😋 Want to balance it with some fruits or a probiotic like curd?",
      "Sounds like a feast! 🥳 For your next meal, consider something light like soup or a sprout salad.",
      "Mmm... I can almost smell it! 🍛 How about swapping fried stuff with grilled or baked options?",
      "That’s great! 🌿 Try keeping your plate colorful — more veggies means more nutrients!"
    ];

    const randomTip = responses[Math.floor(Math.random() * responses.length)];
    return `${randomTip} Need help planning your next meal? 🥗`;
  }

  // Continuing from previous code inside getBotReply...

// 🧠 5. Mood & Wellness Tracker with mood history

const moodKeywords = ["happy", "tired", "anxious", "excited", "angry", "sad"];

// Trigger mood check prompt
if (message.toLowerCase().includes("mood") || message.toLowerCase().includes("feeling") || message.toLowerCase().includes("how are you")) {
  return "Let’s do a quick mood check! 😊 How are you feeling today: happy, tired, anxious, excited, angry, sad, or something else?";
}

const moodTips = {
  happy: "That's wonderful! 🌞 Keep spreading that sunshine. Try sharing a compliment with someone today!",
  tired: "Take a short nap or stretch break 💤. A glass of water or some fresh air might also refresh you.",
  anxious: "Deep breaths, you’ve got this 🌬️. Try a 5-minute meditation or write your thoughts down.",
  excited: "Awesome! 🚀 Channel that energy into something creative or productive today!",
  angry: "Take a deep breath, drink cold water, and walk away for a moment—reset before you react. 🧊🚶‍♀️💨",
  sad: "It's okay to feel this way 😔. Be kind to yourself, maybe listen to your favorite music or talk to a friend."
};

// Detect if user shared their mood explicitly
const detectedMood = moodKeywords.find(mood => message.toLowerCase().includes(mood));

if (detectedMood) {
  // Save mood with timestamp to localStorage
  try {
    const moodHistory = JSON.parse(localStorage.getItem("moodHistory")) || [];
    moodHistory.push({ mood: detectedMood, date: new Date().toISOString() });
    localStorage.setItem("moodHistory", JSON.stringify(moodHistory));
  } catch (err) {
    console.warn("Failed to save mood history:", err);
  }

  return `Thanks for sharing. It's okay to feel ${detectedMood}.\nHere's a wellness tip: ${moodTips[detectedMood]}`;
}

// Mood history summary
if (message.toLowerCase().includes("how was my mood this week") || message.toLowerCase().includes("mood history")) {
  try {
    const moodHistory = JSON.parse(localStorage.getItem("moodHistory")) || [];

    if (moodHistory.length === 0) {
      return "You haven't shared your mood with me yet this week. Try telling me how you're feeling!";
    }

    // Filter moods from last 7 days
    const oneWeekAgo = new Date();
    oneWeekAgo.setDate(oneWeekAgo.getDate() - 7);

    const recentMoods = moodHistory.filter(entry => new Date(entry.date) >= oneWeekAgo);

    if (recentMoods.length === 0) {
      return "No mood data found for the past week. Let's start tracking your mood!";
    }

    // Count occurrences of each mood
    const moodCounts = recentMoods.reduce((counts, entry) => {
      counts[entry.mood] = (counts[entry.mood] || 0) + 1;
      return counts;
    }, {});

    // Create summary string like "happy (3 days), tired (2 days), ..."
    const summary = Object.entries(moodCounts)
      .map(([mood, count]) => `${mood} (${count} day${count > 1 ? 's' : ''})`)
      .join(", ");

    return `Here's your mood summary for the past week: ${summary}. Keep taking care of yourself! 😊`;
  } catch (err) {
    console.warn("Failed to get mood history:", err);
    return "Sorry, I couldn't retrieve your mood history right now.";
  }
}

  // 🧠 6. General Health & Wellness Keywords
const healthKeywords = ["health", "wellness", "exercise", "fitness", "sleep", "hydration", "stress", "nutrition", "diet", "weight", "energy", "immunity"];
if (healthKeywords.some(keyword => message.includes(keyword))) {
  if (message.includes("exercise") || message.includes("fitness")) {
    return "💪 Regular exercise boosts energy and mood! Try 30 mins of walking, yoga, or any activity you enjoy. Start small and build consistency!";
  }
  if (message.includes("sleep")) {
    return "😴 Good sleep is vital! Aim for 7-8 hours, keep your room dark and cool, avoid screens before bed, and try a bedtime routine.";
  }
  if (message.includes("hydration") || message.includes("water")) {
    return "💧 Stay hydrated! Drinking at least 8 glasses of water daily keeps your body and mind sharp. Add lemon or cucumber for flavor!";
  }
  if (message.includes("stress")) {
    return "🧘‍♂️ Feeling stressed? Try deep breathing, meditation, or a short walk to calm your mind. Remember to take breaks!";
  }
  if (message.includes("nutrition") || message.includes("diet")) {
    return "🍎 Balanced nutrition matters. Include fruits, veggies, proteins, and whole grains in your meals. Eat the rainbow for variety!";
  }
  if (message.includes("weight") && message.includes("loss")) {
    return "⚖️ Healthy weight loss: Focus on portion control, regular exercise, and sustainable habits. Aim for 1-2 lbs per week maximum.";
  }
  if (message.includes("energy")) {
    return "⚡ Boost energy naturally: Get enough sleep, stay hydrated, eat regular meals, and include iron-rich foods like spinach and lentils.";
  }
  if (message.includes("immunity")) {
    return "🛡️ Strengthen immunity: Eat vitamin C foods (citrus, berries), get enough sleep, manage stress, and stay active.";
  }
  return "🌟 Maintaining good health is a mix of balanced diet, regular exercise, quality sleep, and staying hydrated. Small consistent changes make a big difference!";
}

// 🎙️ 7. Voice Input
if (message.includes("voice") || message.includes("speak")) {
  return "Great news! 🎙️ Voice input is now enabled. Click the microphone 🎤 button next to the chat box to speak your questions or commands, and I'll respond aloud too! Give it a try.";
}

// 🔐 8. Privacy Info
if (message.includes("privacy") || message.includes("data")) {
  return "Your health data is encrypted 🔐 and stored securely. We never share it without your permission.";
}

// 🛒 9. Shopping List Features
if (message.includes("grocery") || message.includes("shopping list")) {
  return "Let's create your list! 🛒 Just tell me what meals or items you need.";
}

if (/add (.+?) (to( my)? )?(shopping )?list/i.test(message)) {
  const itemMatch = message.match(/add (.+?)(?: to list| on my list)?$/i);
  if (itemMatch) {
    const item = itemMatch[1].trim().toLowerCase();
    try {
      const list = JSON.parse(localStorage.getItem("shoppingList")) || [];

      const alreadyExists = list.some(i => i.item === item);

      if (!alreadyExists) {
        list.push({ item, added: new Date().toLocaleDateString() });
        localStorage.setItem("shoppingList", JSON.stringify(list));
        return `📝 Added "${item}" to your shopping list!`;
      } else {
        return `📋 "${item}" is already on your list.`;
      }
    } catch (err) {
      console.warn("Error accessing shopping list from localStorage:", err);
      return "Oops! I had trouble updating your shopping list. Try again soon.";
    }
  }
}

if (
  message.includes("show list") ||
  message.includes("what's on my list") ||
  message.includes("show my shopping list")
) {
  try {
    const list = JSON.parse(localStorage.getItem("shoppingList")) || [];
    if (list.length === 0)
      return "Your shopping list is empty. 🧺 Add items by saying 'Add oats to list'.";

    return (
      `🛒 Here's your list:\n\n` +
      list
        .map(
          (i) =>
            `• ${i.item.charAt(0).toUpperCase() + i.item.slice(1)} (added on ${i.added})`
        )
        .join("\n")
    );
  } catch (err) {
    console.warn("Error retrieving shopping list:", err);
    return "Sorry, I couldn't retrieve your shopping list right now.";
  }
}

if (message.includes("clear list")) {
  try {
    localStorage.removeItem("shoppingList");
    return "🧹 Your shopping list has been cleared.";
  } catch (err) {
    console.warn("Error clearing shopping list:", err);
    return "Sorry, I couldn't clear your shopping list right now.";
  }
}

// 👋 10. Goodbye
if (message.includes("bye") || message.includes("goodnight")) {
  return "Bye!👋🏻 Take care and stay hydrated! 💧 See you soon 😄!";
}

// 11. Daily Health Reminders opt-in/out
if (message.includes("reminder on") || message.includes("start reminders")) {
  localStorage.setItem("dailyReminderOptIn", "true");
  startDailyReminders();
  return "✅ Daily Health Reminders are ON. I'll remind you to hydrate, stretch, and check your mood throughout the day!";
}

if (message.includes("reminder off") || message.includes("stop reminders")) {
  localStorage.setItem("dailyReminderOptIn", "false");
  stopDailyReminders();
  return "🛑 Daily Health Reminders are OFF. You can turn them back on anytime by saying 'reminder on'.";
}

// 12. Mental wellness games & prompts
const mentalWellnessGames = [
  "🧘 Try a 2-minute mindful breathing: Close your eyes, inhale slowly for 4 seconds, hold for 4, exhale for 4. Repeat 5 times.",
  "🧩 Quick brain teaser: What has keys but can't open locks? (Answer: A piano!)",
  "🎨 Doodle time! Take 2 minutes to draw whatever comes to mind, no judgment.",
  "📚 Write down 3 things you're grateful for right now.",
  "🕵️‍♀️ Spot the difference: Look around you and find 5 things you didn't notice before.",
  "🎯 Challenge: Focus on a single object for 1 minute without letting your mind wander.",
  "🚶‍♂️ Take a quick 5-minute walk, focusing on your surroundings — sounds, colors, smells.",
  "🎵 Sound break: Close your eyes and name 3 different sounds you can hear right now.",
  "📦 Declutter dash: Spend 2 minutes tidying a small area near you.",
  "💌 Kindness note: Write a short message of appreciation to someone you care about.",
  "📝 Prompt: Write a short positive affirmation about yourself.",
  "🍋 Savor it: Take a bite of something and eat it slowly, noticing the flavor and texture.",
  "🎈 Breathe with your hands: Trace the outline of your hand, breathing in on the upstrokes and out on the downstrokes.",
  "🧠 Memory jog: Try to remember and list the last five things you ate or drank today.",
  "🌱 Growth check: Write down one thing you've learned or improved in the last month.",
  "🎭 Emotion check-in: Name what you're feeling right now without judgment.",
  "📷 Mental snapshot: Take a moment to look around and mentally 'photograph' your current space.",
  "💤 Micro-nap: Close your eyes and rest for 2 minutes without sleeping — just breathe and relax.",
  "🌈 Color hunt: Look around and find something red, orange, yellow, green, blue, and purple.",
  "🧦 Texture scan: Touch 3 different objects near you and notice their textures."
];

if (
  message.includes("mental wellness") ||
  message.includes("games") ||
  message.includes("suggest a game") ||
  message.includes("prompts")
) {
  const randomIndex = Math.floor(Math.random() * mentalWellnessGames.length);
  return "Here’s a fun mental wellness game for you: " + mentalWellnessGames[randomIndex];
}

// 13. Natural Remedies Tip
if (
  message.toLowerCase().includes("remedy") ||
  message.toLowerCase().includes("natural cure") ||
  message.toLowerCase().includes("home remedy") ||
  message.toLowerCase().includes("i have a headache") ||
  message.toLowerCase().includes("headache") ||
  message.toLowerCase().includes("cold") ||
  message.toLowerCase().includes("digestion") ||
  message.toLowerCase().includes("stress") ||
  message.toLowerCase().includes("stress remedy") ||
  message.toLowerCase().includes("sleep") ||
  message.toLowerCase().includes("sleep remedy") ||
  message.toLowerCase().includes("cough") ||
  message.toLowerCase().includes("bloating") ||
  message.toLowerCase().includes("menstrual pain") ||
  message.toLowerCase().includes("cramps") ||
  message.toLowerCase().includes("nausea") ||
  message.toLowerCase().includes("dry skin") ||
  message.toLowerCase().includes("indigestion") ||
  message.toLowerCase().includes("eye strain") ||
  message.toLowerCase().includes("sore throat")
) {
  const naturalRemedies = {
    headache: {
      tip: "🧊 Headache Relief: Apply peppermint oil to your temples and massage gently for 1–2 minutes.",
      benefit: "Peppermint contains menthol, which may help relax muscles and ease pain."
    },
    cold: {
      tip: "🍯 Cold Remedy: Mix 1 tsp of honey with warm water and a pinch of turmeric. Sip slowly.",
      benefit: "Honey soothes the throat, and turmeric is anti-inflammatory and immune-boosting."
    },
    digestion: {
      tip: "🫚 Digestion Aid: Chew a small piece of fresh ginger or sip ginger tea after meals.",
      benefit: "Ginger stimulates digestive enzymes and reduces bloating."
    },
    stress: {
      tip: "🫖 Stress Soother: Brew a cup of chamomile or tulsi (holy basil) tea.",
      benefit: "Both herbs are known for their calming properties in Ayurvedic and herbal traditions."
    },
    sleep: {
      tip: "🌙 Sleep Support: Rub a few drops of lavender essential oil on your pillow or wrists.",
      benefit: "Lavender promotes relaxation and may improve sleep quality."
    },
    cough: {
      tip: "🍵 Mix 1 tsp honey with warm water and add a pinch of black pepper. Sip slowly.",
      benefit: "Honey soothes the throat and pepper helps reduce throat irritation."
    },
    bloating: {
      tip: "🌿 Chew a few carom seeds (ajwain) with a pinch of salt after meals.",
      benefit: "Ajwain contains thymol, which helps release stomach acids for better digestion."
    },
    "menstrual pain": {
      tip: "🫖 Drink chamomile or ginger tea during cramps.",
      benefit: "Both herbs help reduce inflammation and relax uterine muscles."
    },
    nausea: {
      tip: "🫚 Suck on a piece of candied ginger or sip ginger tea.",
      benefit: "Ginger has been shown to significantly reduce nausea symptoms."
    },
    "dry skin": {
      tip: "🥥 Apply coconut oil before bed, especially on dry patches.",
      benefit: "Coconut oil locks in moisture and has antibacterial properties."
    },
    indigestion: {
      tip: "🍋 Drink a glass of warm water with lemon juice first thing in the morning.",
      benefit: "Lemon stimulates bile production, aiding digestion and liver detox."
    },
    "eye strain": {
      tip: "👁️ Place a warm compress over closed eyes for 1 - 2 minutes.",
      benefit: "Heat relaxes the eye muscles and improves circulation."
    },
    "sore throat": {
      tip: "🧂 Gargle with warm salt water (½ tsp salt in 1 cup water).",
      benefit: "Saltwater reduces inflammation and helps kill bacteria."
    },
    default: {
      tip: "🌿 Try sipping warm lemon water in the morning to aid detox and digestion.",
      benefit: "Lemon is rich in vitamin C and supports liver function."
    }
  };

  const keys = Object.keys(naturalRemedies);
  const matchedKey = keys.find(key => new RegExp(`\\b${key}\\b`, 'i').test(message));
  const remedy = matchedKey ? naturalRemedies[matchedKey] : naturalRemedies["default"];

  return `🌿 Natural Remedy Tip:\n\n${remedy.tip}\n\n🧠 Why it works: ${remedy.benefit}\n `;
}

// 14. Natural Remedies Tip Reminder Controls
if (message.includes("natural tips on")) {
  localStorage.setItem("dailyNaturalTips", "true");
  startNaturalTipReminders();
  return "🌿 Daily Natural Remedy Tips are ON. You'll get gentle wellness suggestions throughout the day!";
}

if (message.includes("natural tips off")) {
  localStorage.setItem("dailyNaturalTips", "false");
  stopNaturalTipReminders();
  return "🛑 Natural Remedy Tips are OFF. Turn them on again anytime by saying 'natural tips on'.";
}

// 15. Set Reminder Time Manually
const remindMatch = message.match(/remind me every (\d+) hours?/);
if (remindMatch) {
  const hours = parseInt(remindMatch[1], 10);
  if (isNaN(hours) || hours <= 0) {
    return "Please specify a valid number of hours for the reminder.";
  }
  localStorage.setItem("reminderIntervalHours", hours);
  restartDailyReminderTimer(hours);
  return `⏰ Got it! I'll remind you every ${hours} hour(s).`;
}

// 16. Specific Topic Responses
if (message.includes("morning routine")) {
  return "🌅 Morning routine: Start with 5 min stretching, drink a glass of water, have a healthy breakfast, and set 3 intentions for the day. This sets a positive tone!";
}

if (message.includes("healthy snacks")) {
  return "🥜 Healthy snacks: Nuts, fruits, Greek yogurt, hummus with veggies, or a small smoothie. Avoid processed snacks and opt for whole foods!";
}

if (message.includes("meditation")) {
  return "🧘‍♀️ Meditation: Start with 5 min daily. Focus on your breath, use apps like Headspace, or try guided meditations. Even 2 minutes helps!";
}

if (message.includes("back pain")) {
  return "🪑 Back pain relief: Try cat-cow stretches, gentle twists, and avoid sitting for too long. Strengthen your core and maintain good posture.";
}

if (message.includes("anxiety")) {
  return "🌬️ Managing anxiety: Try 4-7-8 breathing (inhale 4, hold 7, exhale 8), grounding techniques, and regular exercise. Consider talking to a professional if it persists.";
}

// 17. Fallback Response
const geminiReply = await askGemini(input);

// 🌟 Smart keyword-to-emoji mapping
let emojiReply = geminiReply
  .replace(/\*/g, "") // remove asterisks
  .replace(/\b(sleep|rest|nap|bedtime)\b/gi, "🛌 $1")
  .replace(/\b(hydrate|water|drink|fluids)\b/gi, "💧 $1")
  .replace(/\b(yoga|stretch|meditate|relax|breathe)\b/gi, "🧘 $1")
  .replace(/\b(walk|exercise|run|cardio|move)\b/gi, "🚶‍♀️ $1")
  .replace(/\b(food|diet|nutrition|eat|snack)\b/gi, "🍎 $1")
  .replace(/\b(mind|mental|stress|calm)\b/gi, "🧠 $1")
  .replace(/\b(happy|smile|joy|cheerful)\b/gi, "😊 $1");
// 🎲 Sprinkle random fun emojis
const funEmojis = ["✨", "🌸", "🌼", "🌈", "🍀", "💫", "🥰", "🌻", "🦋", "🌟"];
const sparkle1 = funEmojis[Math.floor(Math.random() * funEmojis.length)];
const sparkle2 = funEmojis[Math.floor(Math.random() * funEmojis.length)];

// Final decorated reply
const emojiDecoratedReply = `🤖 ${emojiReply.trim()} ${sparkle1} ${sparkle2}`;
return emojiDecoratedReply;


  
} 
// Form submit handler is already defined above, removing duplicate


// --- Auxiliary functions for reminders ---
let reminderInterval = null;
function startDailyReminders() {
  if (reminderInterval) return; // Already running
  const intervalHours = parseInt(localStorage.getItem("reminderIntervalHours")) || 0.5; // default 30 mins
  reminderInterval = setInterval(() => {
    if (localStorage.getItem("dailyReminderOptIn") !== "true") {
      clearInterval(reminderInterval);
      reminderInterval = null;
      return;
    }
    const reminders = [
      "💧 Time to hydrate! Grab a glass of water.",
      "🧘‍♀️ Take a quick stretch break — neck rolls, shoulder shrugs, and deep breaths!",
      "😊 How's your mood right now? Feeling good or need a pick-me-up?",
      "🥗 Don't forget to include some veggies or fruits in your next meal.",
      "🚶‍♂️ Stand up and take a short walk — your body will thank you!",
      "💤 Close your eyes for a moment. Take 3 deep breaths. Reset your mind.",
      "📵 Take a 2-minute tech break — no screens, just stillness.",
      "🥜 Feeling snacky? Grab a handful of nuts or a fruit instead of chips.",
      "🧠 Quick mental check-in: What's one thing you're grateful for right now?"
    ];
    const reminder = reminders[Math.floor(Math.random() * reminders.length)];
    addMessage("bot", reminder);
  }, intervalHours * 10 * 1000); // Convert hours to milliseconds
}
function stopDailyReminders() {
  if (reminderInterval) {
    clearInterval(reminderInterval);
    reminderInterval = null;
  }
}
function restartDailyReminderTimer(hours) {
  stopDailyReminders();
  localStorage.setItem("reminderIntervalHours", hours);
  startDailyReminders();
}

let naturalTipInterval = null;
function startNaturalTipReminders() {
  if (naturalTipInterval) return;
  naturalTipInterval = setInterval(() => {
    if (localStorage.getItem("dailyNaturalTips") !== "true") {
      clearInterval(naturalTipInterval);
      naturalTipInterval = null;
      return;
    }
    const allTips = [
      "🌼 Try drinking fennel tea after meals to ease bloating.",
      "🛁 Add a few drops of eucalyptus oil to a hot shower for sinus relief.",
      "🌙 Rub warm sesame oil on your feet before bed for deeper sleep.",
      "🥤 Start your morning with ajwain (carom seed) water to support digestion.",
      "🍯 Mix honey and a pinch of cinnamon in warm water — it’s a classic immunity booster.",
      "🍋 Start the day with warm lemon water — flushes toxins and wakes up your digestive system.",
      "🌸 Drink rose water with cold milk during summer to cool down your body naturally.",
      "🪔 Apply a drop of castor oil in your navel at night — old-school trick for dry skin relief.",
      "🧄 Chew a raw garlic clove in the morning (if you dare) for its natural antibiotic effects.",
      "🫖 Sip tulsi tea during stressful workdays to stay calm and focused."
    ];

    const randomTip = allTips[Math.floor(Math.random() * allTips.length)];
    addMessage("bot", `🌿 Daily Natural Tip: ${randomTip}`);

  }, 10 * 1000); // Every 4 hours
}
function stopNaturalTipReminders() {
  if (naturalTipInterval) {
    clearInterval(naturalTipInterval);
    naturalTipInterval = null;
  }
}

// Auto-start reminders on load if previously enabled
window.addEventListener("load", () => {
  if (localStorage.getItem("dailyReminderOptIn") === "true") {
    startDailyReminders();
  }
  if (localStorage.getItem("dailyNaturalTips") === "true") {
    startNaturalTipReminders();
  }
});


// ---- Voice Feature Integration ----
let recognizing = false;
let recognition;

// Add event listeners after DOM loads
document.addEventListener("DOMContentLoaded", function () {
  const voiceBtn = document.getElementById("voice-btn");
  const userInput = document.getElementById("user-input");

  // Setup SpeechRecognition
  window.SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (window.SpeechRecognition) {
    recognition = new window.SpeechRecognition();
    recognition.lang = 'en-IN'; // or 'en-US'
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    // Handle recognition results
    recognition.onresult = function(event) {
      const transcript = event.results[0][0].transcript.trim();
      userInput.value = transcript;
      // Optionally submit form automatically:
      setTimeout(() => {
        document.getElementById("chat-form").requestSubmit();
      }, 300);
    };
    recognition.onend = function () {
      recognizing = false;
      micIcon.innerText = "🎤";
    };
    recognition.onerror = function () {
      recognizing = false;
      micIcon.innerText = "🎤";
      alert("Could not access microphone or recognize speech.");
    };

    if (voiceBtn) {
      voiceBtn.addEventListener("click", function () {
        if (!recognizing) {
          recognition.start();
          recognizing = true;
          micIcon.innerText = "⏺️";
        } else {
          recognition.stop();
          micIcon.innerText = "🎤";
        }
      });
    }
  } else if (voiceBtn) {
    voiceBtn.disabled = true;
    micIcon.innerText = "❌";
    voiceBtn.title = "Voice input not supported";
  }
});

function speakBotMessage(text) {
  if (!("speechSynthesis" in window)) return;

  // Allow apostrophes so contractions like "I'll" are spoken correctly
  const filtered = text.replace(/[^\w\s.,?!']/g, " ").replace(/\s\s+/g, " ").trim();
  const utter = new window.SpeechSynthesisUtterance(filtered);
  utter.lang = 'en-IN'; // Adjust as needed

  // Softer, gentle voice settings for clarity and softness
  utter.rate = 1;    
  utter.pitch = 1.15;
  utter.volume = 0.9;

  function setFemaleVoice() {
    const voices = window.speechSynthesis.getVoices();
    if (!voices || voices.length === 0) return false;

    const femaleVoices = voices.filter(voice =>
      voice.lang.startsWith('en') &&
      (voice.name.toLowerCase().includes('zira') ||
       voice.name.toLowerCase().includes('kendra') ||
       voice.name.toLowerCase().includes('victoria') ||
       voice.name.toLowerCase().includes('susan') ||
       voice.name.toLowerCase().includes('female'))
    );

    if (femaleVoices.length > 0) {
      utter.voice = femaleVoices[0];
    } else {
      utter.voice = voices[0];
    }
    return true;
  }

  const voicesReady = setFemaleVoice();

  if (!voicesReady) {
    const onVoicesChanged = () => {
      if (setFemaleVoice()) {
        window.speechSynthesis.speak(utter);
        window.speechSynthesis.onvoiceschanged = null;
      }
    };
    window.speechSynthesis.onvoiceschanged = onVoicesChanged;
  } else {
    window.speechSynthesis.speak(utter);
  }
}


// Patch addMessage to speak bot replies
const origAddMessage = addMessage;
addMessage = function(sender, text) {
  origAddMessage(sender, text);
  if (sender === "bot") {
    speakBotMessage(text);
  }
};
