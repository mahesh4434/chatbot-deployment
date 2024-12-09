const handleSubmit = async (e) => {
  e.preventDefault();
  if (!userInput.trim()) return;

  setMessages([...messages, { text: userInput, isBot: false }]);
  setIsLoading(true);
  setUserInput('');

  const modifiedUserInput = `${userInput} in DevOps`;

  try {
    const response = await axios.post('https://chatbot-deployment-e3gg.vercel.app/process', {
      text: modifiedUserInput,
    });

    const botMessage = response.data.generated_text || 'Sorry, I could not understand that.';
    const formattedBotResponse = formatBotResponse(botMessage);
    setMessages([...messages, { text: userInput, isBot: false }, ...formattedBotResponse]);
  } catch (error) {
    console.error("Error occurred:", error);
    setMessages([...messages, { text: userInput, isBot: false }, { text: 'Error: Could not connect to the server.', isBot: true }]);
  } finally {
    setIsLoading(false);
  }
};
