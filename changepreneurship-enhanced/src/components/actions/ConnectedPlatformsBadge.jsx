import React from 'react';

const PLATFORM_INFO = {
  micromentor: {
    label: 'MicroMentor',
    description: 'Mentor search & outreach',
    icon: '🤝',
  },
  linkedin: {
    label: 'LinkedIn',
    description: 'Professional network',
    icon: '💼',
  },
  email: {
    label: 'Email',
    description: 'Direct email outreach',
    icon: '✉️',
  },
};

export default function ConnectedPlatformsBadge({
  connectedPlatforms = [],
  onConnect,
}) {
  const allPlatforms = Object.keys(PLATFORM_INFO);

  return (
    <div className="space-y-2">
      <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide">
        Connected Platforms
      </p>
      <div className="flex flex-wrap gap-2">
        {allPlatforms.map((platform) => {
          const info = PLATFORM_INFO[platform];
          const connected = connectedPlatforms.includes(platform);

          return (
            <div
              key={platform}
              className={`flex items-center gap-2 rounded-lg border px-3 py-2 ${
                connected
                  ? 'border-green-300 bg-green-50'
                  : 'border-gray-200 bg-gray-50'
              }`}
            >
              <span className="text-base">{info.icon}</span>
              <div>
                <p className="text-xs font-medium text-gray-800">{info.label}</p>
                <p className="text-xs text-gray-500">{info.description}</p>
              </div>
              {connected ? (
                <span className="ml-2 text-xs text-green-600 font-medium">✓</span>
              ) : (
                <button
                  type="button"
                  onClick={() => onConnect?.(platform)}
                  className="ml-2 text-xs text-blue-600 hover:text-blue-800 font-medium"
                >
                  Connect
                </button>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
