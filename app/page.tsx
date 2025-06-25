"use client"

import React, { useState } from "react"
import { Search, Download, Users, MessageSquare, Twitter, Globe, Calendar, MapPin, CheckCircle2, SlidersHorizontal } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import { Separator } from "@/components/ui/separator"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import Image from "next/image"

export default function HomePage() {
  const [usernameInput, setUsernameInput] = useState("")
  const [promptInput, setPromptInput] = useState("")
  const [countInput, setCountInput] = useState("50")
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<{ count: number; followers: any[] } | null>(null)
  const [selectedUser, setSelectedUser] = useState<any>(null)
  const [fetched, setFetched] = useState(0)

  const handleAnalyze = () => {
    setError("")
    setResult(null)
    setFetched(0)

    const usernames = usernameInput
      .split(/[\s,]+/)
      .map((u) => u.trim())
      .filter((u) => u.length)

    if (usernames.length !== 1) {
      setError("Only one username is allowed.")
      return
    }

    const count = parseInt(countInput)
    if (isNaN(count) || count < 1) {
      setError("Please enter a valid number of profiles to filter (minimum 1).")
      return
    }

    setLoading(true)

    const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000"
    const url = `${backendUrl}/api/v1/webscrape-stream?user_request=${encodeURIComponent(
      usernames[0].replace("@", "")
    )}&user_prompt=${encodeURIComponent(promptInput)}&count=${count}`

    const es = new EventSource(url)

    es.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data)
        if (payload.total_fetched !== undefined) {
          setFetched(payload.total_fetched)
        }
      } catch (e) {
        // ignore malformed messages
      }
    }

    es.addEventListener("done", (event) => {
      try {
        const payload = JSON.parse((event as MessageEvent).data)
        setResult(payload)
      } catch (_) {}
      setLoading(false)
      es.close()
    })

    es.addEventListener("error", () => {
      setError("Stream error")
      setLoading(false)
      es.close()
    })
  }

  const downloadCSV = () => {
    if (!result?.followers?.length) return

    const username = usernameInput.trim().replace('@', '')
    const headers = [
      "User ID",
      "Username",
      "Name",
      "Description",
      "Location",
      "Website",
      "Created At",
      "Followers Count",
      "Following Count",
      "Tweets Count",
      "Media Count",
      "Verified",
      "Business Account",
      "Tags",
      "AI Analysis Notes",
      "Bot Score",
    ]

    const rows = result.followers.map((f) => [
      f.user_id || f.id,
      f.screen_name,
      f.name,
      f.description,
      f.location,
      f.website,
      f.created_at,
      f.followers_count,
      f.friends_count,
      f.statuses_count,
      f.media_count,
      f.blue_verified ? "Yes" : "No",
      f.business_account ? "Yes" : "No",
      f.tags,
      f.ai_analysis_notes,
      f.bot_score,
    ])

    const csvContent = [
      headers.join(","),
      ...rows.map((row) => row.map((cell) => `"${(cell || "").toString().replace(/"/g, '""')}"`).join(",")),
    ].join("\n")

    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" })
    const link = document.createElement("a")
    const url = URL.createObjectURL(blob)
    link.setAttribute("href", url)
    link.setAttribute("download", `${username}_analyzed_followers.csv`)
    link.style.visibility = "hidden"
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  return (
    <>
      <div className="min-h-screen bg-gray-50">
        {/* Header */}
        <header className="bg-white border-b border-gray-200">
          <div className="max-w-4xl mx-auto px-4 py-4">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
                <Search className="w-4 h-4 text-white" />
              </div>
              <h1 className="text-2xl font-bold text-gray-900">fanfilter</h1>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="max-w-4xl mx-auto px-4 py-8">
          <div className="space-y-8">
            {/* Hero Section */}
            <div className="text-center space-y-4">
              <h2 className="text-4xl font-bold text-gray-900">Filter X Profiles with AI</h2>
              <p className="text-xl text-gray-600 max-w-2xl mx-auto">
                Enter one username and your filter prompt to get insights about X profiles. Export your results as CSV for
                further filtering.
              </p>
            </div>

            {/* Input Form */}
            <Card className="shadow-sm">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Twitter className="w-5 h-5 text-blue-500" />
                  Filter Followers
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Username Input and Filter Options */}
                <div className="space-y-2">
                  <Label htmlFor="usernames" className="flex items-center gap-2 text-sm font-medium">
                    <Users className="w-4 h-4" />
                    X Username
                  </Label>
                  <div className="flex gap-3 items-start">
                    <div className="flex-1">
                      <Textarea
                        id="usernames"
                        placeholder="Enter one username (example: @elonmusk)"
                        className="min-h-[80px] resize-none"
                        value={usernameInput}
                        onChange={(e) => setUsernameInput(e.target.value)}
                      />
                      <p className="text-xs text-gray-500 mt-1">Please enter exactly one username.</p>
                    </div>
                    <div className="flex flex-col gap-1 min-w-[180px]">
                      <Label className="flex items-center gap-2 text-sm font-medium">
                        <SlidersHorizontal className="w-4 h-4" />
                        Filter Count
                      </Label>
                      <Select value={countInput} onValueChange={setCountInput}>
                        <SelectTrigger>
                          <SelectValue placeholder="Number of profiles" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="20">20 profiles</SelectItem>
                          <SelectItem value="50">50 profiles (default)</SelectItem>
                          <SelectItem value="100">100 profiles</SelectItem>
                          <SelectItem value="200">200 profiles</SelectItem>
                          <SelectItem value="500">500 profiles</SelectItem>
                          <SelectItem value="custom">Custom number...</SelectItem>
                        </SelectContent>
                      </Select>
                      {countInput === 'custom' && (
                        <input
                          type="number"
                          min="1"
                          placeholder="Enter number"
                          className="mt-1 w-full px-3 py-1.5 rounded-md border border-input bg-background text-sm"
                          value={countInput === 'custom' ? '' : countInput}
                          onChange={(e) => {
                            const value = e.target.value;
                            if (value && parseInt(value) > 0) {
                              setCountInput(value);
                            }
                          }}
                        />
                      )}
                      <p className="text-xs text-gray-500">Select or enter number of profiles to filter</p>
                    </div>
                  </div>
                </div>

                <Separator />

                {/* Prompt Input */}
                <div className="space-y-2">
                  <Label htmlFor="prompt" className="flex items-center gap-2 text-sm font-medium">
                    <MessageSquare className="w-4 h-4" />
                    Filter Prompt
                  </Label>
                  <Textarea
                    id="prompt"
                    placeholder="What would you like to filter about this profile?"
                    className="min-h-[100px] resize-none"
                    value={promptInput}
                    onChange={(e) => setPromptInput(e.target.value)}
                  />
                </div>

                {/* Action Button */}
                <Button className="w-full bg-blue-500 hover:bg-blue-600" size="lg" onClick={handleAnalyze} disabled={loading}>
                  <Search className="w-4 h-4 mr-2" />
                  {loading ? (
                    fetched > 0 ? `Fetched ${fetched}` : "Filtering..."
                  ) : (
                    "Filter Profile"
                  )}
                </Button>

                {error && <p className="text-sm text-red-600 text-center">{error}</p>}
              </CardContent>
            </Card>

            {/* Results Section */}
            <Card className="shadow-sm">
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <span className="flex items-center gap-2">
                    <Download className="w-5 h-5 text-green-600" />
                    Filter Results
                  </span>
                  {result?.followers?.length ? (
                    <div className="flex items-center gap-2">
                      <p className="text-sm text-gray-500">Download CSV for full filter details</p>
                      <Button variant="outline" size="sm" onClick={downloadCSV}>
                        <Download className="w-4 h-4 mr-2" />
                        Download CSV
                      </Button>
                    </div>
                  ) : null}
                </CardTitle>
              </CardHeader>
              <CardContent>
                {loading ? (
                  <div className="text-center py-12 text-gray-500">
                    {fetched > 0 ? (
                      <p>Fetched {fetched} followers so far...</p>
                    ) : (
                      <p>Processing...</p>
                    )}
                  </div>
                ) : result ? (
                  <div className="space-y-4">
                    <p className="text-sm text-gray-700">Found {result.count} relevant followers:</p>
                    <ul className="grid gap-2">
                      {result.followers.map((f: any) => (
                        <li
                          key={f.user_id || f.id}
                          className="border rounded p-3 hover:bg-gray-50 cursor-pointer transition-colors"
                          onClick={() => setSelectedUser(f)}
                        >
                          <div className="flex items-center gap-3">
                            {f.profile_image && (
                              <Image
                                src={f.profile_image}
                                alt={f.name}
                                width={48}
                                height={48}
                                className="rounded-full"
                              />
                            )}
                            <div className="flex-1">
                              <div className="flex items-center gap-1">
                                <span className="font-medium">{f.name}</span>
                                {f.blue_verified && <CheckCircle2 className="w-4 h-4 text-blue-500" />}
                              </div>
                              <div className="text-sm text-gray-600">@{f.screen_name}</div>
                              {f.tags && (
                                <div className="flex flex-wrap gap-1 mt-1">
                                  {(Array.isArray(f.tags) ? f.tags : f.tags.split(','))
                                    .filter((tag: string) => tag && tag.trim())
                                    .map((tag: string, index: number) => (
                                      <span
                                        key={index}
                                        className="px-2 py-0.5 bg-blue-100 text-blue-700 text-xs rounded-full"
                                      >
                                        {tag.trim()}
                                      </span>
                                    ))}
                                </div>
                              )}
                            </div>
                          </div>
                        </li>
                      ))}
                    </ul>
                  </div>
                ) : (
                  <div className="text-center py-12 text-gray-500">
                    <Search className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                    <p className="text-lg font-medium mb-2">No filter yet</p>
                    <p className="text-sm">Enter a username and prompt above to start filtering.</p>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Features */}
            <div className="grid md:grid-cols-3 gap-6 mt-12">
              <Card className="text-center p-6">
                <Users className="w-8 h-8 mx-auto mb-3 text-blue-500" />
                <h3 className="font-semibold mb-2">Multiple Profiles</h3>
                <p className="text-sm text-gray-600">Filter single or multiple X profiles at once</p>
              </Card>
              <Card className="text-center p-6">
                <MessageSquare className="w-8 h-8 mx-auto mb-3 text-green-500" />
                <h3 className="font-semibold mb-2">Custom Prompts</h3>
                <p className="text-sm text-gray-600">Ask specific questions about the profiles</p>
              </Card>
              <Card className="text-center p-6">
                <Download className="w-8 h-8 mx-auto mb-3 text-purple-500" />
                <h3 className="font-semibold mb-2">Export Data</h3>
                <p className="text-sm text-gray-600">Download results as CSV for further filtering</p>
              </Card>
            </div>
          </div>
        </main>

        {/* Footer */}
        <footer className="bg-white border-t border-gray-200 mt-16">
          <div className="max-w-4xl mx-auto px-4 py-8">
            <div className="text-center text-gray-500">
              <p>&copy; 2024 fanfilter. Filter X profiles with AI-powered insights.</p>
            </div>
          </div>
        </footer>
      </div>

      <Dialog open={!!selectedUser} onOpenChange={(open) => !open && setSelectedUser(null)}>
        <DialogContent className="sm:max-w-lg">
          <DialogHeader>
            <DialogTitle>Profile Details</DialogTitle>
          </DialogHeader>
          {selectedUser && (
            <div className="space-y-6">
              {/* Header */}
              <div className="flex items-start gap-4">
                {selectedUser.profile_image && (
                  <Image
                    src={selectedUser.profile_image}
                    alt={selectedUser.name}
                    width={64}
                    height={64}
                    className="rounded-full"
                  />
                )}
                <div>
                  <div className="flex items-center gap-1">
                    <h3 className="font-semibold text-lg">{selectedUser.name}</h3>
                    {selectedUser.blue_verified && <CheckCircle2 className="w-5 h-5 text-blue-500" />}
                  </div>
                  <p className="text-gray-600">@{selectedUser.screen_name}</p>
                </div>
              </div>

              {/* Bio */}
              {selectedUser.description && <p className="text-gray-700">{selectedUser.description}</p>}

              {/* Stats Grid */}
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 py-2">
                <div>
                  <div className="font-medium">{selectedUser.followers_count.toLocaleString()}</div>
                  <div className="text-sm text-gray-600">Followers</div>
                </div>
                <div>
                  <div className="font-medium">{selectedUser.friends_count.toLocaleString()}</div>
                  <div className="text-sm text-gray-600">Following</div>
                </div>
                <div>
                  <div className="font-medium">{selectedUser.statuses_count.toLocaleString()}</div>
                  <div className="text-sm text-gray-600">Tweets</div>
                </div>
              </div>

              {/* Additional Info */}
              <div className="space-y-2 text-sm">
                {selectedUser.location && (
                  <div className="flex items-center gap-2 text-gray-600">
                    <MapPin className="w-4 h-4" />
                    {selectedUser.location}
                  </div>
                )}
                {selectedUser.website && (
                  <div className="flex items-center gap-2 text-gray-600">
                    <Globe className="w-4 h-4" />
                    <a href={selectedUser.website} target="_blank" rel="noopener noreferrer" className="text-blue-500 hover:underline">
                      {selectedUser.website}
                    </a>
                  </div>
                )}
                <div className="flex items-center gap-2 text-gray-600">
                  <Calendar className="w-4 h-4" />
                  Joined {new Date(selectedUser.created_at).toLocaleDateString()}
                </div>
              </div>

              {/* Media Stats */}
              <div className="text-sm text-gray-600">
                <div>Media Count: {selectedUser.media_count.toLocaleString()}</div>
                {selectedUser.business_account && <div>Business Account</div>}
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </>
  )
}
