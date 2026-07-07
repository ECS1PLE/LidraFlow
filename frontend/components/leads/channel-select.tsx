type ChannelSelectProps = {
  name?: string;
  defaultValue?: string;
  className?: string;
};

export function ChannelSelect({ name = "channel", defaultValue = "auto", className = "form-input" }: ChannelSelectProps) {
  return (
    <select name={name} defaultValue={defaultValue} className={className}>
      <option value="auto">Автовыбор</option>
      <option value="whatsapp">WhatsApp</option>
      <option value="telegram">Telegram</option>
      <option value="max">MAX</option>
      <option value="vk">VK</option>
    </select>
  );
}
