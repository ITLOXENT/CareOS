import { useEffect, useMemo, useState } from "react";
import {
  Linking,
  SafeAreaView,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
  RefreshControl
} from "react-native";

import type {
  PortalCareCircleMember,
  PortalEpisode,
  PortalEpisodeDetail,
  PortalNotification,
  PortalMeResponse,
} from "@careos/sdk";
import { createPortalClient } from "@careos/sdk";

export default function App() {
  const [apiBaseUrl, setApiBaseUrl] = useState("http://localhost:8000");
  const [inviteToken, setInviteToken] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [apiToken, setApiToken] = useState("");
  const [authStatus, setAuthStatus] = useState("");
  const [patientProfile, setPatientProfile] = useState<PortalMeResponse | null>(null);
  const [episodes, setEpisodes] = useState<PortalEpisode[]>([]);
  const [selectedEpisode, setSelectedEpisode] = useState<PortalEpisodeDetail | null>(null);
  const [notifications, setNotifications] = useState<PortalNotification[]>([]);
  const [careCircle, setCareCircle] = useState<PortalCareCircleMember[]>([]);
  const [unreadOnly, setUnreadOnly] = useState(false);
  const [loadingEpisodes, setLoadingEpisodes] = useState(false);
  const [loadingNotifications, setLoadingNotifications] = useState(false);
  const [refreshing, setRefreshing] = useState(false);

  const portalClient = useMemo(() => {
    return createPortalClient({ baseUrl: apiBaseUrl });
  }, [apiBaseUrl]);

  const deepLinkText = useMemo(() => {
    return "careos://episode/{id}";
  }, []);

  const parseEpisodeId = (url: string | null) => {
    if (!url) {
      return null;
    }
    const match = url.match(/episode\/(\d+)/);
    if (!match) {
      return null;
    }
    return Number(match[1]);
  };

  const handleDeepLink = (url: string | null) => {
    const episodeId = parseEpisodeId(url);
    if (!episodeId || !apiToken) {
      return;
    }
    void fetchEpisodeDetail(episodeId, apiToken);
  };

  useEffect(() => {
    Linking.getInitialURL().then(handleDeepLink).catch(() => undefined);
    const subscription = Linking.addEventListener("url", (event) => {
      handleDeepLink(event.url);
    });
    return () => {
      subscription.remove();
    };
  }, [apiToken]);

  const handleAcceptInvite = async () => {
    if (!inviteToken.trim()) {
      setAuthStatus("Invite token required.");
      return;
    }
    setAuthStatus("Accepting invite...");
    try {
      const payload = await portalClient.acceptInvite({ token: inviteToken.trim() });
      setApiToken(payload.token);
      setAuthStatus("Signed in.");
    } catch (error) {
      setAuthStatus(String(error));
    }
  };

  const handleLogin = async () => {
    if (!email.trim() && !phone.trim()) {
      setAuthStatus("Provide email or phone.");
      return;
    }
    setAuthStatus("Signing in...");
    try {
      const payload = await portalClient.login({
        email: email.trim() || undefined,
        phone: phone.trim() || undefined
      });
      setApiToken(payload.token);
      setAuthStatus("Signed in.");
    } catch (error) {
      setAuthStatus(String(error));
    }
  };

  const handleSignOut = () => {
    setApiToken("");
    setSelectedEpisode(null);
    setEpisodes([]);
    setNotifications([]);
    setPatientProfile(null);
    setCareCircle([]);
    setAuthStatus("Signed out.");
  };

  const fetchPatientProfile = async (token: string) => {
    try {
      const payload = await portalClient.me(token);
      setPatientProfile(payload);
    } catch (error) {
      setAuthStatus(String(error));
    }
  };

  const fetchEpisodes = async (token: string) => {
    setLoadingEpisodes(true);
    try {
      const payload = await portalClient.listEpisodes(token);
      setEpisodes(payload.results ?? []);
    } catch (error) {
      setAuthStatus(String(error));
    } finally {
      setLoadingEpisodes(false);
    }
  };

  const fetchEpisodeDetail = async (episodeId: number, token: string) => {
    setLoadingEpisodes(true);
    try {
      const payload = await portalClient.getEpisode(token, episodeId);
      setSelectedEpisode(payload);
    } catch (error) {
      setAuthStatus(String(error));
    } finally {
      setLoadingEpisodes(false);
    }
  };

  const fetchNotifications = async (token: string) => {
    setLoadingNotifications(true);
    try {
      const payload = await portalClient.listNotifications(token, {
        unread_only: unreadOnly
      });
      setNotifications(payload.results ?? []);
    } catch (error) {
      setAuthStatus(String(error));
    } finally {
      setLoadingNotifications(false);
    }
  };

  const handleMarkRead = async (notificationId: number) => {
    if (!apiToken) {
      return;
    }
    try {
      await portalClient.markNotificationRead(apiToken, notificationId);
      await fetchNotifications(apiToken);
    } catch (error) {
      setAuthStatus(String(error));
    }
  };

  const handleRefresh = async () => {
    if (!apiToken) {
      return;
    }
    setRefreshing(true);
    await Promise.all([
      fetchPatientProfile(apiToken),
      portalClient.listCareCircle(apiToken).then((payload) => setCareCircle(payload.results)),
      fetchEpisodes(apiToken),
      fetchNotifications(apiToken),
    ]);
    setRefreshing(false);
  };

  useEffect(() => {
    if (!apiToken) {
      return;
    }
    fetchPatientProfile(apiToken);
    portalClient
      .listCareCircle(apiToken)
      .then((payload) => setCareCircle(payload.results))
      .catch((error) => setAuthStatus(String(error)));
    fetchEpisodes(apiToken);
    fetchNotifications(apiToken);
  }, [apiToken, unreadOnly]);

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView
        contentContainerStyle={styles.scroll}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={handleRefresh} />}
      >
        <Text style={styles.title}>CareOS Mobile</Text>

        <View style={styles.card}>
          <Text style={styles.sectionTitle}>Portal sign-in</Text>
          <TextInput
            style={styles.input}
            placeholder="API base URL"
            value={apiBaseUrl}
            onChangeText={setApiBaseUrl}
          />
          <TextInput
            style={styles.input}
            placeholder="Invite token (optional)"
            value={inviteToken}
            onChangeText={setInviteToken}
          />
          <TouchableOpacity style={styles.button} onPress={handleAcceptInvite}>
            <Text style={styles.buttonText}>Accept invite</Text>
          </TouchableOpacity>
          <Text style={styles.muted}>Or sign in with email/phone.</Text>
          <TextInput
            style={styles.input}
            placeholder="Email"
            value={email}
            onChangeText={setEmail}
          />
          <TextInput
            style={styles.input}
            placeholder="Phone"
            value={phone}
            onChangeText={setPhone}
          />
          <TouchableOpacity style={styles.button} onPress={handleLogin}>
            <Text style={styles.buttonText}>Sign in</Text>
          </TouchableOpacity>
          {authStatus ? <Text style={styles.muted}>{authStatus}</Text> : null}
          {apiToken ? (
            <TouchableOpacity style={styles.smallButtonAlt} onPress={handleSignOut}>
              <Text style={styles.buttonTextAlt}>Sign out</Text>
            </TouchableOpacity>
          ) : null}
        </View>

        <View style={styles.card}>
          <Text style={styles.sectionTitle}>Patient profile</Text>
          {patientProfile ? (
            <View>
              <Text style={styles.itemTitle}>
                {patientProfile.given_name} {patientProfile.family_name}
              </Text>
              <Text style={styles.muted}>
                {patientProfile.email || patientProfile.phone}
              </Text>
            </View>
          ) : (
            <Text style={styles.muted}>No patient profile loaded.</Text>
          )}
        </View>

        <View style={styles.card}>
          <Text style={styles.sectionTitle}>Care circle</Text>
          {careCircle.map((member) => (
            <View key={member.id} style={styles.row}>
              <View style={styles.flex}>
                <Text style={styles.itemTitle}>{member.person_name}</Text>
                <Text style={styles.muted}>{member.relationship}</Text>
                {member.contact ? <Text style={styles.muted}>{member.contact}</Text> : null}
              </View>
            </View>
          ))}
          {careCircle.length === 0 ? (
            <Text style={styles.muted}>No care circle members.</Text>
          ) : null}
        </View>

        <View style={styles.card}>
          <Text style={styles.sectionTitle}>Episodes (read-only)</Text>
          {loadingEpisodes ? <Text style={styles.muted}>Loading episodes...</Text> : null}
          {selectedEpisode ? (
            <View>
              <Text style={styles.itemTitle}>{selectedEpisode.episode.title}</Text>
              <Text style={styles.muted}>{selectedEpisode.episode.description}</Text>
              <Text style={styles.muted}>Status: {selectedEpisode.episode.status}</Text>
              <Text style={styles.sectionTitle}>Timeline</Text>
              {selectedEpisode.timeline.map((event) => (
                <Text key={event.id} style={styles.muted}>
                  {event.event_type} · {event.from_state ? `${event.from_state} → ` : ""}
                  {event.to_state} · {event.created_at}
                </Text>
              ))}
              <TouchableOpacity
                style={styles.smallButtonAlt}
                onPress={() => setSelectedEpisode(null)}
              >
                <Text style={styles.buttonTextAlt}>Back to list</Text>
              </TouchableOpacity>
            </View>
          ) : (
            episodes.map((episode) => (
              <TouchableOpacity
                key={episode.id}
                style={styles.row}
                onPress={() => apiToken && fetchEpisodeDetail(episode.id, apiToken)}
              >
                <View style={styles.flex}>
                  <Text style={styles.itemTitle}>{episode.title}</Text>
                  <Text style={styles.muted}>{episode.status}</Text>
                </View>
                <Text style={styles.linkText}>View</Text>
              </TouchableOpacity>
            ))
          )}
          {!loadingEpisodes && episodes.length === 0 && !selectedEpisode ? (
            <Text style={styles.muted}>No episodes available.</Text>
          ) : null}
          <Text style={styles.muted}>Deep link format: {deepLinkText}</Text>
        </View>

        <View style={styles.card}>
          <Text style={styles.sectionTitle}>Notifications (read-only)</Text>
          <View style={styles.row}>
            <TouchableOpacity
              style={unreadOnly ? styles.smallButton : styles.smallButtonAlt}
              onPress={() => setUnreadOnly((prev) => !prev)}
            >
              <Text style={unreadOnly ? styles.buttonText : styles.buttonTextAlt}>
                {unreadOnly ? "Unread only" : "All notifications"}
              </Text>
            </TouchableOpacity>
          </View>
          {loadingNotifications ? (
            <Text style={styles.muted}>Loading notifications...</Text>
          ) : null}
          {notifications.map((item) => (
            <View key={item.id} style={styles.row}>
              <View style={styles.flex}>
                <Text style={styles.itemTitle}>{item.title}</Text>
                <Text style={styles.muted}>
                  {item.unread ? "Unread" : "Read"} · {item.created_at}
                </Text>
                {item.body ? <Text style={styles.muted}>{item.body}</Text> : null}
              </View>
              {item.unread ? (
                <TouchableOpacity
                  style={styles.smallButtonAlt}
                  onPress={() => handleMarkRead(item.id)}
                >
                  <Text style={styles.buttonTextAlt}>Mark read</Text>
                </TouchableOpacity>
              ) : null}
            </View>
          ))}
          {!loadingNotifications && notifications.length === 0 ? (
            <Text style={styles.muted}>No notifications.</Text>
          ) : null}
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#f8fafc"
  },
  scroll: {
    padding: 20
  },
  title: {
    fontSize: 24,
    fontWeight: "700",
    marginBottom: 16,
    color: "#0f172a"
  },
  card: {
    backgroundColor: "#ffffff",
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
    shadowColor: "#0f172a",
    shadowOpacity: 0.05,
    shadowRadius: 8,
    shadowOffset: { width: 0, height: 2 }
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: "600",
    marginBottom: 8
  },
  input: {
    borderWidth: 1,
    borderColor: "#cbd5f5",
    borderRadius: 8,
    padding: 10,
    marginBottom: 10
  },
  multiline: {
    minHeight: 80,
    textAlignVertical: "top"
  },
  button: {
    backgroundColor: "#2563eb",
    padding: 10,
    borderRadius: 8,
    alignItems: "center"
  },
  buttonText: {
    color: "#ffffff",
    fontWeight: "600"
  },
  smallButton: {
    backgroundColor: "#2563eb",
    paddingVertical: 6,
    paddingHorizontal: 10,
    borderRadius: 6,
    marginLeft: 8
  },
  smallButtonAlt: {
    backgroundColor: "#e2e8f0",
    paddingVertical: 6,
    paddingHorizontal: 10,
    borderRadius: 6,
    marginLeft: 8
  },
  buttonTextAlt: {
    color: "#0f172a",
    fontWeight: "600"
  },
  row: {
    flexDirection: "row",
    alignItems: "center",
    marginBottom: 8
  },
  flex: {
    flex: 1
  },
  itemTitle: {
    fontWeight: "600"
  },
  linkText: {
    color: "#2563eb",
    fontWeight: "600"
  },
  muted: {
    color: "#64748b"
  },
});
