import React, { useEffect, useState } from "react";

export default function EventsList() {
  const [events, setEvents] = useState([]);
  const [filteredEvents, setFilteredEvents] = useState([]);
  const [eventType, setEventType] = useState("all");

  // Fetch events from backend
  useEffect(() => {
    const fetchEvents = async () => {
      try {
        const response = await fetch("http://localhost:5000/events");
        const data = await response.json();
        setEvents(data);
        setFilteredEvents(data);
      } catch (error) {
        console.error("Failed to fetch events", error);
      }
    };

    fetchEvents();
    const interval = setInterval(fetchEvents, 15000); // Poll every 15 seconds
    return () => clearInterval(interval);
  }, []);

  // Filter events on dropdown change
  useEffect(() => {
    if (eventType === "all") {
      setFilteredEvents(events);
    } else {
      const filtered = events.filter((event) => event.type === eventType);
      setFilteredEvents(filtered);
    }
  }, [eventType, events]);

  const uniqueEventTypes = ["all", ...new Set(events.map((e) => e.type))];

  const formatDate = (input) => {
    if (!input) return "Unknown Date";

    // Handle MongoDB extended JSON: { $date: "..." }
    const isoDate = typeof input === "object" && input.$date ? input.$date : input;
    const date = new Date(isoDate);

    if (isNaN(date.getTime())) return "Invalid Date";

    return date.toLocaleString("en-US", {
      day: "numeric",
      month: "short",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
      timeZone: "UTC",
      hour12: true,
    }) + " UTC";
  };

  const renderMessage = (event) => {
    const { author, type, from_branch, to_branch, timestamp } = event;
    const time = formatDate(timestamp);

    if (type === "push") {
      return `${author} pushed to ${to_branch} on ${time}`;
    } else if (type === "pull_request") {
      return `${author} submitted a pull request from ${from_branch} to ${to_branch} on ${time}`;
    } else if (type === "merge") {
      return `${author} merged branch ${from_branch} to ${to_branch} on ${time}`;
    }
    return "Unknown event";
  };

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <h1 className="text-3xl font-bold mb-6 text-center text-gray-800">
        📦 GitHub Webhook Events
      </h1>

      {/* Filter dropdown */}
      <div className="mb-6 text-center">
        <label className="text-gray-700 font-medium mr-2">Filter by Type:</label>
        <select
          value={eventType}
          onChange={(e) => setEventType(e.target.value)}
          className="px-3 py-1 border border-gray-300 rounded"
        >
          {uniqueEventTypes.map((type) => (
            <option key={type} value={type}>
              {type === "all" ? "All Events" : type}
            </option>
          ))}
        </select>
      </div>

      {/* Events List */}
      <div className="grid gap-4 max-w-3xl mx-auto overflow-y-auto max-h-[80vh]">
        {filteredEvents.length === 0 ? (
          <p className="text-center text-gray-500">No events found.</p>
        ) : (
          filteredEvents.map((event, index) => (
            <div
              key={index}
              className="bg-white shadow-md rounded-xl p-4 border border-gray-200"
            >
              <p className="text-sm text-gray-500 mb-2">
                <strong>ID:</strong> {event._id?.$oid || "N/A"}
              </p>
              <p className="text-gray-800 font-medium">{renderMessage(event)}</p>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
