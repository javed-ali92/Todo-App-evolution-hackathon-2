/**
 * MessageList component for displaying conversation history.
 * Shows user and bot messages with task operation confirmations.
 */

"use client";

import { useEffect, useRef } from "react";
import { Message } from "@/lib/hooks/use-chat";

interface MessageListProps {
  messages: Message[];
  isLoading: boolean;
}

export default function MessageList({ messages, isLoading }: MessageListProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const formatTime = (date: Date) => {
    return new Intl.DateTimeFormat("en-US", {
      hour: "numeric",
      minute: "2-digit",
      hour12: true,
    }).format(date);
  };

  const renderTaskOperation = (taskOperation: any) => {
    if (!taskOperation) return null;

    if (!taskOperation.success) {
      return (
        <div className="mt-2 p-3 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-sm text-red-800">
            ❌ Error: {taskOperation.error || "Operation failed"}
          </p>
        </div>
      );
    }

    // Task created
    if (taskOperation.task) {
      const task = taskOperation.task;
      return (
        <div className="mt-2 p-3 bg-green-50 border border-green-200 rounded-lg">
          <p className="text-sm font-medium text-green-900 mb-2">
            ✅ Task Created
          </p>
          <div className="space-y-1 text-sm text-green-800">
            <p>
              <span className="font-medium">Title:</span> {task.title}
            </p>
            {task.description && (
              <p>
                <span className="font-medium">Description:</span>{" "}
                {task.description}
              </p>
            )}
            {task.due_date && (
              <p>
                <span className="font-medium">Due:</span>{" "}
                {new Date(task.due_date).toLocaleDateString()}
              </p>
            )}
            {task.priority && (
              <p>
                <span className="font-medium">Priority:</span> {task.priority}
              </p>
            )}
          </div>
        </div>
      );
    }

    // Task list
    if (taskOperation.tasks) {
      const tasks = taskOperation.tasks;
      const count = taskOperation.count || tasks.length;

      return (
        <div className="mt-2 p-3 bg-blue-50 border border-blue-200 rounded-lg">
          <p className="text-sm font-medium text-blue-900 mb-2">
            📋 Found {count} task{count !== 1 ? "s" : ""}
          </p>
          {tasks.length > 0 && (
            <div className="space-y-2">
              {tasks.slice(0, 5).map((task: any, index: number) => (
                <div
                  key={task.id || index}
                  className="text-sm text-blue-800 bg-white p-2 rounded border border-blue-100"
                >
                  <p className="font-medium">
                    {task.completed ? "✓" : "○"} {task.title}
                  </p>
                  {task.due_date && (
                    <p className="text-xs text-blue-600 mt-1">
                      Due: {new Date(task.due_date).toLocaleDateString()}
                    </p>
                  )}
                </div>
              ))}
              {tasks.length > 5 && (
                <p className="text-xs text-blue-600 italic">
                  ...and {tasks.length - 5} more
                </p>
              )}
            </div>
          )}
        </div>
      );
    }

    // Task updated/completed/deleted
    if (taskOperation.message) {
      return (
        <div className="mt-2 p-3 bg-blue-50 border border-blue-200 rounded-lg">
          <p className="text-sm text-blue-800">✓ {taskOperation.message}</p>
        </div>
      );
    }

    return null;
  };

  if (messages.length === 0 && !isLoading) {
    return (
      <div className="flex-1 flex items-center justify-center p-8">
        <div className="text-center max-w-md">
          <div className="text-6xl mb-4">💬</div>
          <h3 className="text-xl font-semibold text-gray-700 mb-2">
            Start a conversation
          </h3>
          <p className="text-gray-500 mb-4">
            Ask me to manage your tasks using natural language!
          </p>
          <div className="text-left bg-gray-50 p-4 rounded-lg space-y-2 text-sm text-gray-600">
            <p className="font-medium text-gray-700">Try saying:</p>
            <ul className="space-y-1 ml-4">
              <li>• "Remind me to buy groceries tomorrow"</li>
              <li>• "Show me my tasks"</li>
              <li>• "Mark 'project report' as done"</li>
              <li>• "What do I need to do today?"</li>
            </ul>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-4">
      {messages.map((message) => (
        <div
          key={message.id}
          className={`flex ${
            message.sender === "user" ? "justify-end" : "justify-start"
          }`}
        >
          <div
            className={`max-w-[80%] ${
              message.sender === "user"
                ? "bg-blue-600 text-white"
                : "bg-gray-100 text-gray-900"
            } rounded-lg px-4 py-3 shadow-sm`}
          >
            <div className="flex items-start gap-2">
              <div className="flex-1">
                <p className="text-sm whitespace-pre-wrap break-words">
                  {message.content}
                </p>
                {message.sender === "bot" && message.taskOperation && (
                  <div className="mt-2">
                    {renderTaskOperation(message.taskOperation)}
                  </div>
                )}
              </div>
            </div>
            <p
              className={`text-xs mt-2 ${
                message.sender === "user"
                  ? "text-blue-100"
                  : "text-gray-500"
              }`}
            >
              {formatTime(message.timestamp)}
            </p>
          </div>
        </div>
      ))}

      {isLoading && (
        <div className="flex justify-start">
          <div className="bg-gray-100 rounded-lg px-4 py-3 shadow-sm">
            <div className="flex items-center gap-2">
              <div className="flex space-x-1">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                <div
                  className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                  style={{ animationDelay: "0.1s" }}
                ></div>
                <div
                  className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                  style={{ animationDelay: "0.2s" }}
                ></div>
              </div>
              <span className="text-sm text-gray-500">Thinking...</span>
            </div>
          </div>
        </div>
      )}

      <div ref={messagesEndRef} />
    </div>
  );
}
