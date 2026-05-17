let sentimentChart = null;
let tagChart = null;
let riskChart = null;
let cachedComments = [];


function escapeHtml(value) {
    if (value === null || value === undefined) {
        return "";
    }

    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}


function safeLower(value) {
    return String(value || "").toLowerCase();
}


function parseTags(tagsText) {
    try {
        const tags = JSON.parse(tagsText);

        if (Array.isArray(tags)) {
            return tags;
        }

        return [];
    } catch (e) {
        if (!tagsText) {
            return [];
        }

        return String(tagsText)
            .split(",")
            .map(tag => tag.trim())
            .filter(tag => tag.length > 0);
    }
}


function getElement(id) {
    return document.getElementById(id);
}


async function fetchStats() {
    const response = await fetch("/api/stats");
    const stats = await response.json();

    getElement("total").innerText = stats.total;
    getElement("positive").innerText = stats.positive;
    getElement("negative").innerText = stats.negative;
    getElement("neutral").innerText = stats.neutral;
    getElement("highRisk").innerText = stats.high_risk;

    updateChart(stats);
}


async function fetchAnalysisSummary() {
    const response = await fetch("/api/analysis-summary");
    const summary = await response.json();

    const summaryText = getElement("analysisSummaryText");
    const positiveRate = getElement("summaryPositiveRate");
    const negativeRate = getElement("summaryNegativeRate");
    const neutralRate = getElement("summaryNeutralRate");
    const highRiskRate = getElement("summaryHighRiskRate");

    if (summaryText) {
        summaryText.innerText = summary.summary_text || "Analiz özeti oluşturulamadı.";
    }

    if (positiveRate) {
        positiveRate.innerText = `${summary.positive_rate || 0}%`;
    }

    if (negativeRate) {
        negativeRate.innerText = `${summary.negative_rate || 0}%`;
    }

    if (neutralRate) {
        neutralRate.innerText = `${summary.neutral_rate || 0}%`;
    }

    if (highRiskRate) {
        highRiskRate.innerText = `${summary.high_risk_rate || 0}%`;
    }
}


async function fetchTagStats() {
    const response = await fetch("/api/tag-stats");
    const items = await response.json();

    updateTagChart(Array.isArray(items) ? items : []);
}


function updateTagChart(items) {
    const ctx = getElement("tagChart");

    if (!ctx) {
        return;
    }

    const labels = items.map(item => item.tag);
    const data = items.map(item => item.count);

    if (tagChart !== null) {
        tagChart.destroy();
    }

    tagChart = new Chart(ctx, {
        type: "bar",
        data: {
            labels: labels,
            datasets: [{
                label: "Etiket Sayısı",
                data: data,
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            indexAxis: "y",
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    ticks: {
                        precision: 0
                    }
                }
            }
        }
    });
}


async function fetchRiskStats() {
    const response = await fetch("/api/risk-stats");
    const stats = await response.json();

    updateRiskChart(stats || {});
}


function updateRiskChart(stats) {
    const ctx = getElement("riskChart");

    if (!ctx) {
        return;
    }

    const labels = ["Düşük", "Orta", "Yüksek", "Kritik"];

    const data = [
        stats.low || 0,
        stats.medium || 0,
        stats.high || 0,
        stats.critical || 0
    ];

    if (riskChart !== null) {
        riskChart.destroy();
    }

    riskChart = new Chart(ctx, {
        type: "doughnut",
        data: {
            labels: labels,
            datasets: [{
                label: "Risk Sayısı",
                data: data,
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: "bottom"
                }
            }
        }
    });
}


async function fetchUserRiskStats() {
    const response = await fetch("/api/user-risk-stats");
    const users = await response.json();

    const container = getElement("userRiskList");

    if (!container) {
        return;
    }

    container.innerHTML = "";

    if (!Array.isArray(users) || users.length === 0) {
        container.innerHTML = "<p class='empty-text'>Kullanıcı bazlı analiz için veri bulunmuyor.</p>";
        return;
    }

    users.forEach(user => {
        const item = document.createElement("div");
        item.className = "user-risk-item";

        item.innerHTML = `
            <div class="user-risk-main">
                <div class="user-avatar">
                    <i class="fa-solid fa-user"></i>
                </div>

                <div>
                    <strong>${escapeHtml(user.author_username)}</strong>
                    <span>Toplam yorum: ${escapeHtml(user.total_comments)}</span>
                </div>
            </div>

            <div class="user-risk-stats">
                <span>Olumsuz: <b>${escapeHtml(user.negative_comments)}</b></span>
                <span>Orta: <b>${escapeHtml(user.medium_risk_comments)}</b></span>
                <span>Yüksek: <b>${escapeHtml(user.high_risk_comments)}</b></span>
                <span>Kritik: <b>${escapeHtml(user.critical_risk_comments)}</b></span>
                <span>Max Skor: <b>${escapeHtml(user.max_risk_score)}</b></span>
                <span>Ort. Skor: <b>${escapeHtml(user.avg_risk_score)}</b></span>
            </div>
        `;

        container.appendChild(item);
    });
}


async function fetchWordStats() {
    const response = await fetch("/api/word-stats");
    const words = await response.json();

    const container = getElement("wordList");

    if (!container) {
        return;
    }

    container.innerHTML = "";

    if (!Array.isArray(words) || words.length === 0) {
        container.innerHTML = "<p class='empty-text'>Kelime analizi için veri bulunmuyor.</p>";
        return;
    }

    words.forEach(item => {
        const chip = document.createElement("div");
        chip.className = "word-chip";

        chip.innerHTML = `
            <span>${escapeHtml(item.word)}</span>
            <b>${escapeHtml(item.count)}</b>
        `;

        container.appendChild(chip);
    });
}

async function fetchSpamAnalysis() {
    const response = await fetch("/api/spam-analysis");
    const data = await response.json();

    renderRepeatedMessages(data.repeated_messages || []);
    renderSpamUsers(data.spam_users || []);
}


function renderRepeatedMessages(messages) {
    const container = getElement("repeatedMessagesList");

    if (!container) {
        return;
    }

    container.innerHTML = "";

    if (!Array.isArray(messages) || messages.length === 0) {
        container.innerHTML = "<p class='empty-text'>Tekrarlanan mesaj bulunmuyor.</p>";
        return;
    }

    messages.forEach(item => {
        const div = document.createElement("div");
        div.className = "spam-item";

        const usersText = Array.isArray(item.users)
            ? item.users.join(", ")
            : "";

        div.innerHTML = `
            <div class="spam-item-top">
                <strong>Tekrar: ${escapeHtml(item.repeat_count)}</strong>
                <span>Kullanıcı: ${escapeHtml(item.user_count)}</span>
            </div>

            <p>${escapeHtml(item.comment_text)}</p>

            <small>
                ${escapeHtml(item.platform)} | ${escapeHtml(item.latest_time)}
            </small>

            <div class="spam-users-mini">
                ${escapeHtml(usersText)}
            </div>
        `;

        container.appendChild(div);
    });
}


function renderSpamUsers(users) {
    const container = getElement("spamUsersList");

    if (!container) {
        return;
    }

    container.innerHTML = "";

    if (!Array.isArray(users) || users.length === 0) {
        container.innerHTML = "<p class='empty-text'>Spam şüpheli kullanıcı bulunmuyor.</p>";
        return;
    }

    users.forEach(user => {
        const div = document.createElement("div");
        div.className = `spam-user-item ${escapeHtml(user.spam_level)}`;

        div.innerHTML = `
            <div class="spam-user-header">
                <div>
                    <strong>${escapeHtml(user.author_username)}</strong>
                    <span>${escapeHtml(user.platform)}</span>
                </div>

                <b>Skor: ${escapeHtml(user.spam_score)}</b>
            </div>

            <p>${escapeHtml(user.example_comment)}</p>

            <div class="spam-user-stats">
                <span>Toplam: <b>${escapeHtml(user.total_comments)}</b></span>
                <span>Tekrar: <b>${escapeHtml(user.duplicate_comment_count)}</b></span>
                <span>Aynı mesaj: <b>${escapeHtml(user.max_same_comment_count)}</b></span>
                <span>Link: <b>${escapeHtml(user.link_count)}</b></span>
            </div>
        `;

        container.appendChild(div);
    });
}


async function fetchSourceStatus() {
    const response = await fetch("/api/source-status");
    const status = await response.json();

    const activeSources = [];

    if (status.use_youtube) {
        activeSources.push(status.youtube_configured ? "YouTube aktif" : "YouTube key bekliyor");
    }

    if (status.use_x) {
        activeSources.push(status.x_configured ? "X aktif" : "X token bekliyor");
    }

    if (status.use_instagram) {
        activeSources.push(status.instagram_configured ? "Instagram aktif" : "Instagram token bekliyor");
    }

    if (status.use_fake) {
        activeSources.push("Simülasyon verisi aktif");
    }

    if (activeSources.length === 0) {
        activeSources.push("Aktif kaynak yok");
    }

    getElement("sourceStatusText").innerText = activeSources.join(" | ");

    setStatusBadge("youtubeConfigured", status.youtube_configured, status.use_youtube);
    setStatusBadge("xConfigured", status.x_configured, status.use_x);
    setStatusBadge("instagramConfigured", status.instagram_configured, status.use_instagram);
}


function setStatusBadge(elementId, configured, active) {
    const element = getElement(elementId);

    if (!element) {
        return;
    }

    if (!active) {
        element.innerText = "Kapalı";
        element.className = "status-dot";
        return;
    }

    if (configured) {
        element.innerText = "Hazır";
        element.className = "status-dot ready";
    } else {
        element.innerText = "Key gerekli";
        element.className = "status-dot warning";
    }
}


async function loadApiConfig() {
    const response = await fetch("/api/config");
    const config = await response.json();

    

    getElement("useFake").checked = config.use_fake;

    getElement("useYoutube").checked = config.use_youtube;
    getElement("youtubeVideoIds").value = config.youtube_video_ids || "";
    getElement("youtubePollSeconds").value = config.youtube_poll_seconds || 60;
    getElement("youtubeMaxResults").value = config.youtube_max_results || 100;
    if (getElement("youtubeChannelInput")) {
    getElement("youtubeChannelInput").value = config.youtube_channel_input || "@maunmedya";
}

if (getElement("youtubeChannelVideoLimit")) {
    getElement("youtubeChannelVideoLimit").value = config.youtube_channel_video_limit || 40;
}

if (getElement("youtubeAutoFetchChannelVideos")) {
    getElement("youtubeAutoFetchChannelVideos").checked = config.youtube_auto_fetch_channel_videos !== false;
}

    getElement("useX").checked = config.use_x;
    getElement("xSearchQuery").value = config.x_search_query || "";
    getElement("xPollSeconds").value = config.x_poll_seconds || 60;

    getElement("useInstagram").checked = config.use_instagram;
    getElement("instagramMediaIds").value = config.instagram_media_ids || "";
    getElement("instagramPollSeconds").value = config.instagram_poll_seconds || 60;
}


async function saveApiConfig()
 {
    const payload = {
        use_fake: getElement("useFake").checked,

        use_youtube: getElement("useYoutube").checked,
youtube_api_key: getElement("youtubeApiKey").value.trim(),
youtube_video_ids: getElement("youtubeVideoIds").value.trim(),
youtube_poll_seconds: Number(getElement("youtubePollSeconds").value || 60),
youtube_max_results: Number(getElement("youtubeMaxResults").value || 100),
youtube_auto_fetch_channel_videos: getElement("youtubeAutoFetchChannelVideos")?.checked || false,
youtube_channel_input: getElement("youtubeChannelInput")?.value.trim() || "@maunmedya",
youtube_channel_video_limit: Number(getElement("youtubeChannelVideoLimit")?.value || 40),

        use_x: getElement("useX").checked,
        x_bearer_token: getElement("xBearerToken").value.trim(),
        x_search_query: getElement("xSearchQuery").value.trim(),
        x_poll_seconds: Number(getElement("xPollSeconds").value || 60),

        use_instagram: getElement("useInstagram").checked,
        instagram_access_token: getElement("instagramAccessToken").value.trim(),
        instagram_media_ids: getElement("instagramMediaIds").value.trim(),
        instagram_poll_seconds: Number(getElement("instagramPollSeconds").value || 60)

        
    };

    const response = await fetch("/api/config", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(payload)
    });

    const result = await response.json();

    getElement("youtubeApiKey").value = "";
    getElement("xBearerToken").value = "";
    getElement("instagramAccessToken").value = "";

    alert(result.message);

    await loadApiConfig();
    await fetchSourceStatus();
}

async function fetchYoutubeChannelVideos() {
    const button = document.querySelector(".channel-fetch-btn");
    const oldText = button ? button.innerHTML : "";

    if (button) {
        button.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i><span>Video ID’ler çekiliyor...</span>`;
        button.disabled = true;
    }

    await saveApiConfig();

    try {
        const response = await fetch("/api/youtube-channel-videos");
        const result = await response.json();

        if (!result.success) {
            alert(result.message || "Video ID çekilemedi.");
            return;
        }

        const videoIdsInput = getElement("youtubeVideoIds");

        if (videoIdsInput) {
            videoIdsInput.value = result.video_ids || "";
        }

        alert(result.message);

    } catch (error) {
        alert("Kanal video ID çekme sırasında hata oluştu.");
        console.error(error);
    } finally {
        if (button) {
            button.innerHTML = oldText;
            button.disabled = false;
        }
    }
}
async function fetchComments() {
    const response = await fetch("/api/comments");
    const comments = await response.json();

    cachedComments = Array.isArray(comments) ? comments : [];

    updateDynamicFilters();
    renderComments();
}


function updateDynamicFilters() {
    const platformSelect = getElement("platformFilter");
    const tagSelect = getElement("tagFilter");

    if (!platformSelect || !tagSelect) {
        return;
    }

    const selectedPlatform = platformSelect.value || "all";
    const selectedTag = tagSelect.value || "all";

    const platforms = [...new Set(
        cachedComments
            .map(comment => comment.platform)
            .filter(platform => platform && String(platform).trim() !== "")
    )].sort();

    const tagSet = new Set();

    cachedComments.forEach(comment => {
        parseTags(comment.tags).forEach(tag => {
            if (tag && String(tag).trim() !== "") {
                tagSet.add(tag);
            }
        });
    });

    const tags = [...tagSet].sort();

    platformSelect.innerHTML = "";
    tagSelect.innerHTML = "";

    const allPlatformOption = document.createElement("option");
    allPlatformOption.value = "all";
    allPlatformOption.textContent = "Tümü";
    platformSelect.appendChild(allPlatformOption);

    platforms.forEach(platform => {
        const option = document.createElement("option");
        option.value = platform;
        option.textContent = platform;
        platformSelect.appendChild(option);
    });

    const allTagOption = document.createElement("option");
    allTagOption.value = "all";
    allTagOption.textContent = "Tümü";
    tagSelect.appendChild(allTagOption);

    tags.forEach(tag => {
        const option = document.createElement("option");
        option.value = tag;
        option.textContent = tag;
        tagSelect.appendChild(option);
    });

    if ([...platformSelect.options].some(option => option.value === selectedPlatform)) {
        platformSelect.value = selectedPlatform;
    } else {
        platformSelect.value = "all";
    }

    if ([...tagSelect.options].some(option => option.value === selectedTag)) {
        tagSelect.value = selectedTag;
    } else {
        tagSelect.value = "all";
    }
}


function getFilteredAndSortedComments() {
    const searchValue = safeLower(getElement("commentSearch")?.value);
    const sentimentFilter = getElement("sentimentFilter")?.value || "all";
    const riskFilter = getElement("riskFilter")?.value || "all";
    const platformFilter = getElement("platformFilter")?.value || "all";
    const tagFilter = getElement("tagFilter")?.value || "all";
    const sortFilter = getElement("sortFilter")?.value || "newest";
    const dateStartFilter = getElement("dateStartFilter")?.value || "";
const dateEndFilter = getElement("dateEndFilter")?.value || "";

    let filteredComments = cachedComments.filter(comment => {
        const tags = parseTags(comment.tags);

        const searchText = safeLower(`
            ${comment.comment_text || ""}
            ${comment.author_username || ""}
            ${comment.platform || ""}
            ${comment.sentiment || ""}
            ${comment.risk_level || ""}
            ${tags.join(" ")}
        `);

        const matchesSearch = searchText.includes(searchValue);
        const matchesSentiment = sentimentFilter === "all" || comment.sentiment === sentimentFilter;
        const matchesRisk = riskFilter === "all" || comment.risk_level === riskFilter;
        const matchesPlatform = platformFilter === "all" || comment.platform === platformFilter;
        const matchesTag = tagFilter === "all" || tags.includes(tagFilter);

const commentDate = String(comment.collected_at || comment.created_at || "").slice(0, 10);

const matchesStartDate =
    dateStartFilter === "" || commentDate >= dateStartFilter;

const matchesEndDate =
    dateEndFilter === "" || commentDate <= dateEndFilter;

return (
    matchesSearch &&
    matchesSentiment &&
    matchesRisk &&
    matchesPlatform &&
    matchesTag &&
    matchesStartDate &&
    matchesEndDate
);
    });

    const sentimentOrderPositive = {
        positive: 1,
        neutral: 2,
        negative: 3
    };

    const sentimentOrderNegative = {
        negative: 1,
        neutral: 2,
        positive: 3
    };

    filteredComments.sort((a, b) => {
        const idA = Number(a.id || 0);
        const idB = Number(b.id || 0);

        if (sortFilter === "oldest") {
            return idA - idB;
        }

        if (sortFilter === "risk_desc") {
            return Number(b.risk_score || 0) - Number(a.risk_score || 0);
        }

        if (sortFilter === "risk_asc") {
            return Number(a.risk_score || 0) - Number(b.risk_score || 0);
        }

        if (sortFilter === "positive_first") {
            return (sentimentOrderPositive[a.sentiment] || 99) - (sentimentOrderPositive[b.sentiment] || 99);
        }

        if (sortFilter === "negative_first") {
            return (sentimentOrderNegative[a.sentiment] || 99) - (sentimentOrderNegative[b.sentiment] || 99);
        }

        return idB - idA;
    });

    return filteredComments;
}


function buildSourceUrl(comment) {
    if (comment.source_url && String(comment.source_url).trim() !== "") {
        return comment.source_url;
    }

    const externalId = String(comment.external_id || "");

    if (comment.platform === "YouTube" && externalId.startsWith("youtube_")) {
        const raw = externalId.replace("youtube_", "");
        const videoId = raw.substring(0, 11);
        const commentId = raw.substring(12);

        if (videoId) {
            if (commentId) {
                return `https://www.youtube.com/watch?v=${encodeURIComponent(videoId)}&lc=${encodeURIComponent(commentId)}`;
            }

            return `https://www.youtube.com/watch?v=${encodeURIComponent(videoId)}`;
        }
    }

    if (comment.platform === "X" && externalId.startsWith("x_")) {
        const tweetId = externalId.replace("x_", "");
        const username = comment.author_username || "i";

        if (tweetId) {
            return `https://x.com/${encodeURIComponent(username)}/status/${encodeURIComponent(tweetId)}`;
        }
    }

    return "";
}


function renderComments() {
    const table = getElement("commentsTable");

    if (!table) {
        return;
    }

    const filteredComments = getFilteredAndSortedComments();

    table.innerHTML = "";

    if (filteredComments.length === 0) {
        table.innerHTML = `
            <tr>
                <td colspan="9" class="empty-table">
                    Seçilen filtrelere uygun yorum bulunamadı.
                </td>
            </tr>
        `;
        return;
    }

    filteredComments.forEach(comment => {
        const tags = parseTags(comment.tags);
        const row = document.createElement("tr");

        const sourceUrl = buildSourceUrl(comment);

        const sourceButton = sourceUrl
            ? `<a class="source-link" href="${escapeHtml(sourceUrl)}" target="_blank" rel="noopener noreferrer">
                    <i class="fa-solid fa-arrow-up-right-from-square"></i>
                    Git
               </a>`
            : `<span class="source-empty">Yok</span>`;

        row.innerHTML = `
            <td>${escapeHtml(comment.collected_at)}</td>
            <td>${escapeHtml(comment.platform)}</td>
            <td>${escapeHtml(comment.author_username)}</td>
            <td class="comment-cell">${escapeHtml(comment.comment_text)}</td>
            <td><span class="badge ${escapeHtml(comment.sentiment)}">${translateSentiment(comment.sentiment)}</span></td>
            <td><span class="badge ${escapeHtml(comment.risk_level)}">${translateRisk(comment.risk_level)}</span></td>
            <td>${escapeHtml(comment.risk_score)}</td>
            <td>${escapeHtml(tags.join(", "))}</td>
            <td>${sourceButton}</td>
        `;

        table.appendChild(row);
    });
}


function resetFilters() {
    const commentSearch = getElement("commentSearch");
    const sentimentFilter = getElement("sentimentFilter");
    const riskFilter = getElement("riskFilter");
    const platformFilter = getElement("platformFilter");
    const tagFilter = getElement("tagFilter");
    const sortFilter = getElement("sortFilter");
    const dateStartFilter = getElement("dateStartFilter");
const dateEndFilter = getElement("dateEndFilter");

    if (commentSearch) commentSearch.value = "";
    if (sentimentFilter) sentimentFilter.value = "all";
    if (riskFilter) riskFilter.value = "all";
    if (platformFilter) platformFilter.value = "all";
    if (tagFilter) tagFilter.value = "all";
    if (sortFilter) sortFilter.value = "newest";
    if (dateStartFilter) dateStartFilter.value = "";
if (dateEndFilter) dateEndFilter.value = "";

    renderComments();
}


function bindFilterEvents() {
    const filterIds = [
    "commentSearch",
    "sentimentFilter",
    "riskFilter",
    "platformFilter",
    "tagFilter",
    "dateStartFilter",
    "dateEndFilter",
    "sortFilter"
];

    filterIds.forEach(id => {
        const element = getElement(id);

        if (!element) {
            return;
        }

        element.addEventListener("input", renderComments);
        element.addEventListener("change", renderComments);
    });

    const resetButton = getElement("resetFiltersBtn");

    if (resetButton) {
        resetButton.addEventListener("click", function (event) {
            event.preventDefault();
            resetFilters();
        });
    }
}


async function fetchRiskyComments() {
    const response = await fetch("/api/risky-comments");
    const comments = await response.json();

    const container = getElement("riskyComments");

    if (!container) {
        return;
    }

    container.innerHTML = "";

    if (!Array.isArray(comments) || comments.length === 0) {
        container.innerHTML = "<p class='empty-text'>Şu anda yüksek riskli yorum bulunmuyor.</p>";
        return;
    }

    comments.forEach(comment => {
        const item = document.createElement("div");
        item.className = "risk-item";

        item.innerHTML = `
            <strong>${escapeHtml(translateRisk(comment.risk_level))} - Skor: ${escapeHtml(comment.risk_score)}</strong>
            <p>${escapeHtml(comment.comment_text)}</p>
            <small>${escapeHtml(comment.author_username)} | ${escapeHtml(comment.collected_at)}</small>
        `;

        container.appendChild(item);
    });
}


function updateChart(stats) {
    const ctx = getElement("sentimentChart");

    if (!ctx) {
        return;
    }

    const data = {
        labels: ["Olumlu", "Olumsuz", "Nötr"],
        datasets: [{
            label: "Yorum Sayısı",
            data: [stats.positive, stats.negative, stats.neutral],
            borderWidth: 2
        }]
    };

    if (sentimentChart !== null) {
        sentimentChart.destroy();
    }

    sentimentChart = new Chart(ctx, {
        type: "doughnut",
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: "bottom"
                }
            }
        }
    });
}


function translateSentiment(value) {
    if (value === "positive") return "Olumlu";
    if (value === "negative") return "Olumsuz";
    return "Nötr";
}


function translateRisk(value) {
    if (value === "critical") return "Kritik";
    if (value === "high") return "Yüksek";
    if (value === "medium") return "Orta";
    return "Düşük";
}


async function addFakeComment() {
    await fetch("/api/fake-comment", {
        method: "POST"
    });

    await loadDashboard();
}


async function clearComments() {
    const confirmed = confirm("Tüm yorumlar silinsin mi?");

    if (!confirmed) {
        return;
    }

    await fetch("/api/comments", {
        method: "DELETE"
    });

    await loadDashboard();
}


async function loadDashboard() {
    await Promise.allSettled([
        fetchStats(),
        fetchAnalysisSummary(),
        fetchSourceStatus(),
        fetchComments(),
        fetchRiskyComments(),
        fetchTagStats(),
        fetchRiskStats(),
        fetchUserRiskStats(),
        fetchWordStats(),
        fetchSpamAnalysis()
    ]);
}

async function init() {
    bindFilterEvents();
    showUpdateModalOnFirstVisit();
    await loadApiConfig();
    await loadDashboard();
}


document.addEventListener("DOMContentLoaded", init);

function closeUpdateModal() {
    const modal = document.getElementById("updateModal");

    if (!modal) {
        return;
    }

    modal.classList.add("hidden");
    sessionStorage.setItem("maun_update_modal_seen_v2", "true");
}


function showUpdateModalOnFirstVisit() {
    const modal = document.getElementById("updateModal");

    if (!modal) {
        return;
    }

    const alreadySeen = sessionStorage.getItem("maun_update_modal_seen_v2");

    if (alreadySeen === "true") {
        modal.classList.add("hidden");
        return;
    }

    setTimeout(() => {
        modal.classList.remove("hidden");
    }, 600);
}

setInterval(loadDashboard, 3000);