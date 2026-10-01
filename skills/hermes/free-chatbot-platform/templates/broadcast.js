const { createClient } = require('@supabase/supabase-js');
const twilio = require('twilio');

const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_SERVICE_ROLE_KEY
);
const twilioClient = twilio(
  process.env.TWILIO_SID,
  process.env.TWILIO_AUTH_TOKEN
);

async function run() {
  const { data: contacts, error } = await supabase
    .from('contacts')
    .select('whatsapp_number, telegram_id, name')
    .not('whatsapp_number', 'is', null);

  if (error) throw error;

  for (const c of contacts) {
    // WhatsApp template (you must have an approved template in Twilio)
    await twilioClient.messages.create({
      from: 'whatsapp:+141****8886', // sandbox
      to: `whatsapp:${c.whatsapp_number}`,
      body: `Hi ${c.name || 'there'}, this is your weekly health tip!`
    });

    // Telegram (if you have the ID)
    if (c.telegram_id) {
      // Use node-telegram-bot-api or plain HTTP POST
      const telegramToken = process.env.TELEGRAM_TOKEN;
      await fetch(`https://api.telegram.org/bot${telegramToken}/sendMessage`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          chat_id: c.telegram_id,
          text: `Hi ${c.name || 'there'}, this is your weekly health tip!`
        })
      });
    }
  }
}
run().catch(console.error);