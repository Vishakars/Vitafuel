// client/scripts/profile.js
document.addEventListener('DOMContentLoaded', () => {
  // 1) CONFIG
  const deriveApiBase = () => {
    if (window.API_BASE_URL) return window.API_BASE_URL;
    if (window.location.port && window.location.port !== '3000') {
      return `${window.location.origin}/api`;
    }
    return `${window.location.protocol}//${window.location.hostname}:8005/api`;
  };
  const API_BASE_URL = deriveApiBase();
  const SERVER_URL = window.API_BASE_ORIGIN || API_BASE_URL.replace(/\/api$/, '');
  const accessToken = localStorage.getItem('accessToken');

  // Auth guard
  if (!accessToken) {
    alert('Authentication failed. Please log in to access your profile.');
    window.location.href = 'login.html';
    return;
  }

  // 2) DOM references (ids must exist in profile.html)
  const profileForm = document.getElementById('profile-form');
  const nameEl = document.getElementById('name');
  const emailEl = document.getElementById('email');
  const dobEl = document.getElementById('dob');
  const ageEl = document.getElementById('age');
  const heightValueEl = document.getElementById('heightValue');
  const heightUnitEl = document.getElementById('heightUnit');
  const genderEl = document.getElementById('gender');
  const domainsSelect = document.getElementById('healthDomains');
  const avatarPreview = document.getElementById('avatarPreview');
  const avatarUpload = document.getElementById('avatarUpload');

  // 3) Helpers
  const authHeaders = () => ({ 'Authorization': `Bearer ${accessToken}` });
  const setVal = (el, v) => { if (el) el.value = v ?? ''; };
  const setTextOrVal = (el, v) => { if (!el) return; if ('value' in el) el.value = v ?? ''; else el.textContent = v ?? ''; };
  const calcAge = (yyyyMmDd) => {
    if (!yyyyMmDd) return '';
    const birth = new Date(yyyyMmDd);
    const now = new Date();
    let age = now.getFullYear() - birth.getFullYear();
    const m = now.getMonth() - birth.getMonth();
    if (m < 0 || (m === 0 && now.getDate() < birth.getDate())) age--;
    return age;
  };
  const initials = (fullName) => {
    if (!fullName) return 'VF';
    const p = fullName.trim().split(' ').filter(Boolean);
    return (p[0][0] + (p[p.length - 1]?.[0] || '')).toUpperCase();
  };

  // 4) Fetch current user
  const fetchProfileData = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/profile/me`, { headers: authHeaders() });
      if (!res.ok) throw new Error('Failed to load profile data from the server.');
      const data = await res.json();
      populateProfileForm(data);
    } catch (err) {
      console.error('❌ Error fetching profile data:', err);
      alert('Could not load your profile. ' + err.message);
    }
  };

  // 5) Populate UI from backend document
  const populateProfileForm = (userData) => {
    if (!userData) return;
    const profile = userData.profile || {};
    const demo = profile.demographics || {};

    // Build full name from firstName/lastName, fallback to userData.name
    const fullName = `${demo.firstName || ''} ${demo.lastName || ''}`.trim() || userData.name || '';
    setVal(nameEl, fullName);
    setVal(emailEl, userData.email || '');

    // DOB and age
    const dobISO = (demo.dob || '').slice(0, 10);
    setVal(dobEl, dobISO);
    setVal(ageEl, dobISO ? calcAge(dobISO) : '');

    // Height and unit (db stores number of cm)
    setVal(heightValueEl, demo.height ?? '');
    if (heightUnitEl) heightUnitEl.value = 'cm';

    // Gender
    setVal(genderEl, demo.gender || '');

    // Health domains (db stores as [{name, ...}])
    const selected = new Set((profile.healthDomains || []).map(d => d.name));
    if (domainsSelect) {
      Array.from(domainsSelect.options).forEach(opt => {
        opt.selected = selected.has(opt.value);
      });
      if (window.$ && $(domainsSelect).data('select2')) $(domainsSelect).trigger('change');
    }

    // Avatar
    const avatarUrl = profile.avatarUrl ? `${SERVER_URL}${profile.avatarUrl}` : '';
    if (avatarPreview) {
      if (avatarUrl) {
        avatarPreview.style.backgroundImage = `url(${avatarUrl})`;
        avatarPreview.textContent = '';
      } else {
        avatarPreview.style.backgroundImage = '';
        avatarPreview.textContent = initials(fullName);
      }
    }
  };

  // 6) Avatar upload for current user (token identifies the user)
  if (avatarUpload) {
    avatarUpload.addEventListener('change', async (e) => {
      const file = e.target.files?.[0];
      if (!file) return;

      // instant preview
      const reader = new FileReader();
      reader.onload = (ev) => {
        if (avatarPreview) {
          avatarPreview.style.backgroundImage = `url(${ev.target.result})`;
          avatarPreview.textContent = '';
        }
      };
      reader.readAsDataURL(file);

      const formData = new FormData();
      formData.append('file', file); // must match backend UploadFile = File(...)

      try {
        const res = await fetch(`${API_BASE_URL}/profile/avatar`, {
          method: 'PATCH',
          headers: authHeaders(),
          body: formData
        });
        if (!res.ok) throw new Error('Failed to upload avatar.');
        const data = await res.json();
        // If backend returns avatarUrl, set it
        if (data.avatarUrl && avatarPreview) {
          const full = `${SERVER_URL}${data.avatarUrl}`;
          avatarPreview.style.backgroundImage = `url(${full})`;
          avatarPreview.textContent = '';
        }
        alert('Avatar updated successfully!');
      } catch (err) {
        console.error('❌ Avatar upload error:', err);
        alert('Error: ' + err.message);
        fetchProfileData();
      }
    });
  }

  // 7) Save profile updates for current user
  if (profileForm) {
    profileForm.addEventListener('submit', async (e) => {
      e.preventDefault();

      // Split full name
      const [firstName, ...rest] = (nameEl?.value || '').trim().split(' ');
      const lastName = rest.join(' ');

      // Selected health domain values from <select multiple>
      const selectedDomains = domainsSelect
        ? Array.from(domainsSelect.selectedOptions).map(o => o.value)
        : [];

      // Build payload matching backend expectations
      const profileUpdateData = {
        demographics: {
          firstName,
          lastName,
          dob: dobEl?.value || '',
          gender: genderEl?.value || '',
          height: Number(heightValueEl?.value) || null
        },
        healthDomains: selectedDomains
      };

      try {
        // Your backend uses POST "/" to create/update current user’s profile
        const res = await fetch(`${API_BASE_URL}/profile`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            ...authHeaders()
          },
          body: JSON.stringify(profileUpdateData)
        });
        if (!res.ok) {
          const errJson = await res.json().catch(() => ({}));
          throw new Error(errJson.detail || 'Failed to update profile.');
        }
        alert('Profile details saved successfully!');
        fetchProfileData(); // refresh view
      } catch (err) {
        console.error('❌ Profile update error:', err);
        alert('Error: ' + err.message);
      }
    });
  }

  // 8) Init
  fetchProfileData();
});
