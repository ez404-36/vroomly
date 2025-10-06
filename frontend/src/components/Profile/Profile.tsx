import { useNavigate } from "react-router-dom";

const Profile = () => {
  const navigate = useNavigate();

  return (
    <>
      <div>Profile Здесь!</div>
      <br />
      <button onClick={() => navigate(-1)}>Назад</button>
    </>
  );
};

export default Profile;